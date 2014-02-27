#!/usr/local/bin python
# -*- coding:utf-8 -*-

import random
import csv
from XCSConfig import *
from XCSEnvironment import *
from XCSClassifier import *
from XCSClassifierSet import *
from XCSMatchSet import *
from XCSActionSet import *

class XCSProgram:
    def __init__(self):
        self.env = XCSEnvironment()
    def init(self):
        self.env = XCSEnvironment()
    def run_experiments(self):
        for exp in range(conf.max_experiments):
            random.seed(exp)
            self.actual_time = 0.0
            self.pop = XCSClassifierSet(self.env,self.actual_time)
            self.init()
            for iteration in range(conf.max_iterations):
                self.run_explor()
            print "now" + str(exp)
            self.file_writer(exp)
    def run_explor(self):
        self.env.set_state()
        self.match_set = XCSMatchSet(self.pop,self.env,self.actual_time)
        self.generate_prediction_array()
        self.select_action()
        self.action_set = XCSActionSet(self.match_set,self.action,self.env,self.actual_time)
        self.action_set.do_action()
        self.action_set.update_action_set()
        self.action_set.do_action_set_subsumption(self.pop)
        self.run_GA()
        if len(self.pop.cls) > conf.N:
            self.pop.delete_from_population()
        self.actual_time += 1.0

    def select_action(self):
        if random.random() > conf.p_explr:
            self.action = self.best_action()
        else:
            self.action = random.randrange(2)
    def best_action(self):
        big = self.p_array[0]
        best = 0
        for i in range(2):
            if big < self.p_array[i]:
                big = self.p_array[i]
                best = i
        return best
    def generate_prediction_array(self):
        self.p_array = [0,0]
        self.f_array = [0,0]
        for cl in self.match_set.cls:
            self.p_array[cl.action] += cl.prediction*cl.fitness
            self.f_array[cl.action] += cl.fitness
        for i in range(2):
            if self.f_array[i] != 0:
                self.p_array[i] /= self.f_array[i]
    def select_offspring(self):
        fit_sum = self.action_set.fitness_sum()
        choice_point = fit_sum * random.random()
        fit_sum = 0.0
        for cl in self.action_set.cls:
            fit_sum += cl.fitness
            if fit_sum > choice_point:
                return cl
        return None
    def apply_crossover(self,cl1,cl2):
        length = len(cl1.condition)
        sep1 = int(random.random()*(length))
        sep2 = int(random.random()*(length))
        if sep1>sep2:
            tmp = sep1
            sep1 = sep2
            sep2 = tmp
        # elif sep1==sep2:
            # sep2 = sep2+1
        cond1 = cl1.condition
        cond2 = cl2.condition
        for i in range(sep1,sep2):
            if cond1[i] != cond2[i]:
                tmp   = cond1[i]
                cond1[i]= cond2[i]
                cond2[i]= tmp
        cl1.condition = cond1
        cl2.condition = cond2
    def apply_mutation(self,cl):
        i = 0
        for i in range(len(cl.condition)):
            if random.random() < conf.myu:
                if cl.condition[i] == '#':
                    cl.condition[i] = self.env.state[i]
                else:
                    cl.condition[i] = '#'
        if random.random() < conf.myu:
            cl.action = random.randrange(2)
    def run_GA(self):
        if self.actual_time - self.action_set.ts_num_sum()/self.action_set.numerosity_sum()>conf.theta_ga:
            for cl in self.action_set.cls:
                cl.time_stamp = self.actual_time
            parent1 = self.select_offspring()
            parent2 = self.select_offspring()
            child1 = parent1.deep_copy(self.actual_time)
            child2 = parent2.deep_copy(self.actual_time)
            child1.numerosity = 1
            child2.numerosity = 1
            child1.experience = 0
            child2.experience = 0
            if random.random() < conf.chi:
                self.apply_crossover(child1,child2)
                child1.prediction = (parent1.prediction+parent2.prediction)/2.0
                child1.error = 0.25*(parent1.error+parent2.error)/2.0
                child1.fitness = 0.1*(parent1.fitness+parent2.fitness)/2.0
                child2.prediction = child1.prediction
                child2.error = child1.error
                child2.fitness = child1.fitness
            self.apply_mutation(child1)
            self.apply_mutation(child2)
            if conf.doGASubsumption:
                if parent1.does_subsume(child1):
                    parent1.numerosity += 1
                elif parent2.does_subsume(child1):
                    parent2.numerosity += 1
                else:
                    self.pop.insert_in_population(child1)
                if parent1.does_subsume(child2):
                    parent1.numerosity += 1
                elif parent2.does_subsume(child2):
                    parent2.numerosity += 1
                else:
                    self.pop.insert_in_population(child2)
            else:
                self.pop.insert_in_population(child1)
                self.pop.insert_in_population(child2)

            while self.pop.numerosity_sum() > conf.N:
                self.pop.delete_from_population()
    def file_writer(self,num):
        file_name = "population"+str(num)+".csv"
        write_csv = csv.writer(file(file_name,'w'),lineterminator='\n')
        write_csv.writerow(["condition","action","fitness","prediction"])
        for cl in self.pop.cls:
            cond = ""
            for c in cl.condition:
                cond += str(c)
            write_csv.writerow([cond,cl.action,cl.fitness,cl.prediction])
if __name__ == '__main__':
    xcs = XCSProgram()
    xcs.run_experiments()









