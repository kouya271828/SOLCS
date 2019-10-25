# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 11:24:13 2019

@author: Nakata Koya
"""
import pickle
import numpy as np
import matplotlib.pyplot as plt
import SOM

class FigureGenerater():
    def __init__(self, resultDirStr=SOM.conf.dirStr_result()):
        self.resultDirStr = resultDirStr
        with open(self.resultDirStr +  "\\nodes.bin", "rb") as nodes:
            self.nodes = pickle.load(nodes)        
        
        self.actNodesRealNum = self.nodes[:,-1].reshape(SOM.conf.N, SOM.conf.N)
        self.actNodes = np.round(self.actNodesRealNum)
        self.correctActNodes = SOM.getAnsNodes(np.round(self.nodes))
        self.afterNodesRounded_hamming = SOM.getColoredNodes(np.round(self.nodes),
                                        color="bits-scale")
        self.afterNodesRounded = SOM.getColoredNodes(np.round(self.nodes),
                                        color="bits2decimal-scale")
    
        self.afterNodesReverse = np.round(self.nodes)[:,0:-1] #get 6bit nodes
        self.afterNodesReverse = SOM.getColoredNodes(self.afterNodesReverse[:,::-1], color="bits2decimal-scale")
    
        self.afterNodesSeparated = self.afterNodesRounded.copy()
        self.afterNodesColored = SOM.getColoredNodes(np.round(self.nodes), color="colored")        
    
    def genFig(self, doesShow=True):
        """
        Showing map
        """
        dt_now = SOM.conf.dt_now()
        dirStr_result = SOM.conf.dirStr_result()
        
        """
        #plt.figure()
        #plt.imshow(iniCorrectActNodes, cmap="gray", vmin=0, vmax=1, interpolation="none")
        #plt.title("initial map of actions")
        #plt.savefig(dirStr_result + "\\initial map of actions.png")
        
        #plt.figure()
        #plt.imshow(iniNodes, cmap="gray", vmin=0, vmax=63, interpolation="none")
        #plt.title("initial map of condition by 64 scale")
        #plt.savefig(dirStr_result + str(seed) + "\\initial map of condition by 64 scale")
        
        #plt.figure()
        #plt.imshow(iniNodesColored, cmap="gray", vmin=0, vmax=255, interpolation="none")
        #plt.title("initial map colored by address bit")
        #plt.savefig(dirStr_result + "\\initial map colored by address bit")
        """
        
        """
        plt.figure()
        plt.imshow(actNodesR, cmap="gray", vmin=0, vmax=1,
                   interpolation="none")
        plt.title("map of action part after leaning(continuous value)")
        plt.savefig(dirStr_result + 
                    "\\map of action part after leaning(countinuous value)")
        """
        
        plt.figure()
        plt.imshow(self.actNodes, cmap="gray", vmin=0, vmax=1,
                   interpolation="none")
        plt.title("map of action part after leaning")
        plt.savefig(dirStr_result +
                    "\\map of action part after leaning" 
                    + dt_now)
        
        plt.figure()
        plt.imshow(self.correctActNodes, cmap="gray", vmin=0, vmax=1, interpolation="none")
        plt.title("map of correct action part after leaning")
        plt.savefig(dirStr_result +
                    "\\map of correct action part after leaning"
                    + dt_now)
    
        plt.figure()
        plt.imshow(self.afterNodesRounded_hamming, cmap="gray", vmin=0, vmax=5, interpolation="none")
        plt.title("map of condition part after learning scaled by Hamming distance")
        plt.colorbar()
        plt.savefig(dirStr_result +
                    "\\map of condition part after learning scaled by Hamming distance"
                    + dt_now)
        
        plt.figure()
        plt.imshow(self.afterNodesRounded, cmap="gray", vmin=0, vmax=63, interpolation="none")
        plt.title("map of condition part after learning")
        plt.colorbar()
        plt.savefig(dirStr_result +
                    "\\map of condition part after learning"
                    + dt_now)
        
        plt.figure()
        plt.imshow(self.afterNodesReverse , cmap="gray", vmin=0, vmax=63, interpolation="none")
        plt.title("map of condition part after learning(reversed value)")
        plt.colorbar()
        plt.savefig(dirStr_result +
                    "\\map of condition part after learning(reversed value)" 
                    + dt_now)
        
        #afterNodesSeparatedの値を行動の0,1に応じて色分け
        for i, row in enumerate(self.actNodes): #debug: correctActNodesでは正解行動に応じtえ色分けされてしまう
            for j, ans in enumerate(row):
                if ans == 1.0:
                    None
                elif ans == 0.0:
                    #val = afterNodesSeparated[i,j]
                    #afterNodesSeparated[i,j] = -val
                    self.afterNodesSeparated[i,j] = -self.afterNodesSeparated[i,j]
                    
        plt.figure()
        plt.imshow(self.afterNodesSeparated, cmap="PuOr", vmin=-64, vmax=63, interpolation="none")
        plt.title("map of condition part separated by action")
        plt.colorbar()
        plt.savefig(dirStr_result +
                    "\\map of condition part separated by action" 
                    + dt_now)
        
        plt.figure()
        plt.imshow(self.afterNodesColored, cmap="gray", vmin=0, vmax=255, interpolation="none")
        plt.title("map after learning coloerd by address and act")
        plt.savefig(dirStr_result +
                    "\\map after learning coloerd by address and act" 
                    + dt_now)
        
        if doesShow == True:
            plt.show()
    
"""
        #全分類子のマッピング
        main.som.head = None
        
        #mappingDataList = np.array(generateMUXNodes(100,includeAns=True))
        mappingDataSequencial = []
        for i in range(0,64):
            mappingDataSequencial.append(str(bin(i))[2:].zfill(6))
            
        mappingDataSequencial = [list(x) for x in mappingDataSequencial]
        for i, row in enumerate(mappingDataSequencial):
            mappingDataSequencial[i] = [int(x) for x in row]
        
        for cl in mappingDataSequencial:
            cl.append(getAns(cl))
        
        mappingDataSequencial = np.array(mappingDataSequencial).reshape(len(mappingDataSequencial),len(mappingDataSequencial[0]))
"""

"""        
        #実数ノードに全入力を曝露したデータ
        nodes_mapped_new_input = main.som.mapping(mappingDataSequencial)
        
        nodes_mapped_new_input_colored = getColoredNodes(nodes_mapped_new_input, color="colored")
    
        plt.figure()
        plt.imshow(nodes_mapped_new_input_colored, cmap="gray", vmin=0, vmax=255, interpolation="none")
        plt.title("map of new classifier input")
        plt.savefig(dirStr_result +
                    "\\map of new classifier input" 
                    + dt_now)
"""   
   
"""  
        #00‐1領域に現れた不正解分類子の分析
        mappingDataSequencial_000 = []
        for i in range(0,8):
            mappingDataSequencial_000.append(str(bin(i))[2:].zfill(6))
            
        mappingDataSequencial_000 = [list(x) for x in mappingDataSequencial_000]
        
        for i, row in enumerate(mappingDataSequencial_000):
            mappingDataSequencial_000[i] = [int(x) for x in row]
            mappingDataSequencial_000[i].append(1)
            
        mappingDataSequencial_000 = np.delete(mappingDataSequencial_000,5,0)
            
        nodes_mapped_incorrect_input = main.som.mapping(mappingDataSequencial_000, isRounded = True)
        
        nodes_mapped_incorrect_input_colored = getColoredNodes(nodes_mapped_incorrect_input, color="colored")
        
        plt.figure()
        plt.imshow(nodes_mapped_incorrect_input_colored, cmap="gray", vmin=0, vmax=255, interpolation="none")
        plt.title("map of incorrect classifier")
        plt.savefig(dirStr_result +
                    "\\map of incorrect classifier" 
                    + dt_now)
"""

        #plt.show()
        
if __name__ == "__main__":
    #FigureGenerater(default = seed10).genFig()
    FigureGenerater().genFig()