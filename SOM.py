# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 15:36:50 2019

@author: Nakata Koya
"""

import numpy as np
import os
import math
import pickle
#import pprint
import SOLCSConfig as conf
import SOLCSFigureGenerator as fg
import SOLCSAnalyseNodes as a
#import SOLCS_entropy as entropy
from tqdm import tqdm
#from itertools import groupby
from operator import itemgetter
#from numba.decorators import jit

ADBIT00 = [0,1,2]
ADBIT01 = [0,1,3]
ADBIT10 = [0,1,4]
ADBIT11 = [0,1,5]
ADBIT_IDX = {"BLACK":[0,1,2], "RED":[0,1,3], "GREEN":[0,1,4], "BLUE":[0,1,5]}

ADBIT_VALS = [[0,0,0], [0,0,1], [0,1,0], [0,1,1], [1,0,0], [1,0,1], [1,1,0], [1,1,1]]
ACTIONS = [0,1]

class SOM():
    def __init__(self, teachers, N, upd_bit = conf.ADBIT00, head=None, seed=None, doesErrorCorrect = False):
        #seed setting
        if seed==None:
            None
        else: #seedが設定されている
            np.random.seed(seed)
        
        self.teachers = np.array(teachers)
        self.n_teacher = self.teachers.shape[0]
        self.head = head
        self.N = N
        self.upd_bit = upd_bit
        self.doesErrorCorrect = doesErrorCorrect
        
        #格子点の生成
        x, y = np.meshgrid(range(self.N), range(self.N))
        #座標の配列に変換
        self.c = np.hstack((y
                            .flatten()[:, np.newaxis],x.flatten()[:, np.newaxis]))
        #初期マップの生成 caution:11月11日まで行動もランダムに与えていた！
        self.nodes = np.round(np.random.rand(self.N*self.N, self.teachers.shape[1]))
        
        #正解行動の付与 note:このブロックを消せば行動はランダムで与えられる
        for cl in self.nodes:
            cl[-1] = getAns(cl)
            
        self.ininodes = np.copy(self.nodes)
        
        self.unique_dic_dic = {}
            
        #得点の付与
        #for cl in self.nodes:
        #    cl.append(1000*cl[-1])
            
        #entropy
        #self.entropy_list = []
            
    def train(self):
        print("training has started.")

        #hack
        for i, teacher in enumerate(tqdm(self.teachers, position=0, desc="te:"+str(conf.seed_teacher)+" tr"+str(conf.seed_train))):
            bmu = self._best_matching_unit(teacher)
            d = np.linalg.norm(self.c - bmu, axis=1) #cとbmuのmap上での距離
            L = self._learning_ratio(i)
            S = self._learning_radius(i, d)
            
            #ユニークルールセット
            if i%1000 == 0:
                unique_dic_ = a.unique_dic(np.round(self.nodes))
                self.unique_dic_dic[i] = unique_dic_
            
            #teacher[self.head:-2] = 0 #先頭3ビット＋行動だけ更新する場合
            #todo:                                                                                            
            self.nodes[:,self.upd_bit] +=  L * S[:, np.newaxis] * (teacher[self.upd_bit] - self.nodes[:,self.upd_bit])

            #全ビット更新
            #self.nodes +=  L * S[:, np.newaxis] * (teacher - self.nodes)
            
            #誤り訂正　正解行動を付与
            #todo bottle neck
            if self.doesErrorCorrect:
                self.nodes[:,-1] = getAnsNodes(np.round(self.nodes))

        print("training has finished")
        return self.nodes

    def mapping(self, mappingDataList, isRounded=False):
        tmpNodes = self.nodes
        
        if isRounded == True:
            self.nodes = np.round(self.nodes)
        
        #todo
        mapped = np.full((self.N, self.N, self.teachers.shape[1]), -1)
        for i, cl in enumerate(mappingDataList):
            idx = self._best_matching_unit(cl, allIdx=True)
            mapped[idx] = cl
            
        self.nodes = tmpNodes
        
        return mapped.reshape(self.N*self.N, self.teachers.shape[1])
        
    def _best_matching_unit(self, teacher, allIdx=False):
        if self.head == None:
            norms = np.linalg.norm(self.nodes[:, :self.head] - teacher[:self.head], axis=1)
        else: #self.head != None
            #todo
            idx = list(range(self.head)) + [-1]
            nodes = self.nodes[:,idx]
            teacher = teacher[idx]
            #ここで1ビットだけ1000倍のオーダーだったらノルムにどう響く?
            norms = np.linalg.norm(nodes - teacher, axis=1)

        if allIdx == False:
            #最初に見つかったインデックスを一つだけ返す
            bmu = np.argmin(norms) #normsを1次元にreshapeしたときのインデックス
        else:
            #全てのインデックスを返す
            bmu = np.where(norms == norms.min())
            
        return np.unravel_index(bmu,(self.N, self.N)) #N*N行列のargmin

    def _neighbourhood(self, t):#neighbourhood radious
        halflife = float(self.n_teacher/4) #for testing
        initial  = float(self.N/2)
        return initial*np.exp(-t/halflife)

    def _learning_ratio(self, t):
        halflife = float(self.n_teacher/4) #for testing
        initial  = 0.1
        return initial*np.exp(-t/halflife)

    def _learning_radius(self, t, d):
        # d is distance from BMU
        s = self._neighbourhood(t)
        return np.exp(-d**2/(2*s**2))

            
def generateMUXNodes(num_teachers, seed=None, k=2, P_sharp = 0, includeAns = False, includeRewards = False):
    #seed setting
    if seed==None:
        None
    else: #seedが設定されている
        np.random.seed(seed)
        
    teachers = []
    bits = k + 2**k
    for i in range(num_teachers):
        teacher = []
        
        #問題を生成
        for j in range(bits):
            if np.random.rand() < P_sharp:
                teacher.append("#")
            else:
                teacher.append(np.random.randint(2))
                
        #必要なら答えを付与
        if includeAns == True:
            teacher.append(getAns(teacher))
            
        #必要なら報酬を付与
        if includeRewards == True:
            teacher.append(getAns(teacher)*1000)

        teachers.append(teacher)
    return teachers

def getAns(bitArray):
    addbit = bitArray[:conf.k]
    #refbit = bitArray[k:]
    #cal = ""
    #正解行動
    #for x in range(len(addbit)):
    #    cal += str(int(addbit[x]))

    #cal = int(cal,2)
    #ans = refbit[cal]
    #return ans
        
    #return refbit[int(cal,2)]
    return bitArray[conf.k+int("".join(map(str, map(int, addbit))),2)]
    #return bitArray[conf.k+int("".join([str(int(x)) for x in addbit]),2)]

#act含む/含まない両方対応
def getAnsNodes(nodes): #nodes.shape must be [N*N, bits]
    #ansNodes = []
    #for cl in nodes:
    #    ansNodes.append(getAns(cl))
            
    #ansNodes = np.array(ansNodes)
    #return ansNodes.reshape(conf.N, conf.N)
    return np.array(list(map(getAns, nodes))) #mapで高速化できるか?
    #return np.array([getAns(cl) for cl in nodes])

#todo: fgにお引越し
def getColoredNodes(nodes, k=2, color="gray"): #nodes.shape must be [N*N, bits]
    Max = k + k**2
    N = int(math.sqrt(nodes.shape[0])) #edge length of the map
    coloredNodes = []
    
    #アドレスビットと行動で色分け
    if color=="colored":
        for cl in nodes:
            addBits = None
            ansBit = None
            if cl[0] != -1:
                addBitsArray = cl[:k]
                #refBitsArray = cl[k:-1]
                addBits = [str(int(i)) for i in addBitsArray]
                addBits = "".join(addBits)
                #ansBit = refBitsArray[int(addBits,2)] #正解行動
                #todo
                ansBit = cl[-1] #SOMが獲得した正解

            if addBits=="00": #黒
                if ansBit == 1:
                    coloredNodes.append([0,0,0])
                else:
                    coloredNodes.append([128,128,128])    
            elif addBits=="01": #R
                if ansBit == 1:
                    coloredNodes.append([128,0,0])
                else:
                    coloredNodes.append([255,0,0])
            elif addBits=="10": #G
                if ansBit == 1:
                    coloredNodes.append([0,128,0])
                else:
                    coloredNodes.append([0,255,0])
            elif addBits=="11": #B
                if ansBit == 1:
                    coloredNodes.append([0,0,128])
                else:
                    coloredNodes.append([0,0,255])
            else: #W
                coloredNodes.append([255,255,255])

        coloredNodes = np.array(coloredNodes, dtype = np.uint8)
        return coloredNodes.reshape(N, N, 3)
    
    elif color == "bits-scale":
        for cl in nodes:        
            coloredNodes.append(np.sum(cl[:-1])/Max)
            
        coloredNodes = np.array(coloredNodes)
        return coloredNodes.reshape(N, N)

    elif color == "bits2decimal-scale":
        for cl in nodes:
            cljoined = [str(int(i)) for i in cl]
            cljoined = cljoined[:k+k**2] #act bitを除外
            cljoined = "".join(cljoined)
            clIntScale = int(cljoined,2) #2進数の2
            coloredNodes.append(clIntScale)
            #coloredNodes.append(int("".join([str(int(i)) for i in cl]))) #一行で書けばこう
            
        #coloredNodes = np.array(coloredNodes, dtype = np.uint8)
        coloredNodes = np.array(coloredNodes)
        return coloredNodes.reshape(N, N)
    else:
        raise ValueError("colorに渡す引数が間違ってるよ")

    raise ValueError("colorに渡す引数が間違ってるよ")


class Main():
    def __init__(self, upd_bit=conf.ADBIT00):
        os.makedirs(conf.dirStr_result() ,exist_ok=True)            
        self.teachers = generateMUXNodes(seed=conf.seed_teacher, k=conf.k, includeAns=conf.includeAns, num_teachers=conf.num_teachers, includeRewards = conf.includeRewards)        
        self.som = SOM(self.teachers, N=conf.N, upd_bit=upd_bit, head=conf.head, seed=conf.seed_train, doesErrorCorrect = conf.doesErrorCorrect)

    def main(self):
        self.som.train() #som.nodes.shape = (N*N=100*100, bits=7)
        
        #結果をpickleに保存
        with open(conf.dirStr_result() + "\\" + "nodes.bin", "wb") as nodes:
            pickle.dump(self.som.nodes, nodes)        
                  
        with open(conf.dirStr_result() + "\\" + "ininodes.bin", "wb") as ininodes:
            pickle.dump(self.som.ininodes, ininodes)
           
        with open(conf.dirStr_result() + "\\" + "unique_dic_dic.bin", "wb") as dic:
            pickle.dump(self.som.unique_dic_dic, dic)
            
        a.save_unique_cls_dic_dic_as_txt(self.som.unique_dic_dic, conf.dirStr_result())
                    
        

        #how to load
        #with open("nodes.bin", "rb") as nodes:
        #   nodes = pickle.load(nodes)        

if __name__ == "__main__":
    pass