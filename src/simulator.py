# This module contains functions and classes for the main algorithm of generating a simulator.

from turtle import end_fill
import numpy as np
from backlog import Backlog
from work_item import WorkItem
from release_plan import ReleasePlan
from release_scenario import ReleaseScenario
import numpy_financial as npf

class ReleasePlanSimulator():
    def __init__(self, backlog, H, capacity, L, r, B, N):
        self.backlog = backlog
        self.H = H
        self.capacity = capacity  # list of length H
        self.L = L
        self.r = r
        self.B = B
        self.N = N
        self.effort_simulation = self.generateEffortSimulation()#dictionaries
        self.value_simulation = self.generateValueSimulation()

    #effort and value simulation are dictionaries
    #to access, use effort_simulation[w][number of iteration]
    def generateEffortSimulation(self):
        simulation_dict = {}
        for w in self.backlog.work_items:
            [min, mode, max] = w.effort_est
            simulation_dict[w] = np.random.default_rng().triangular(min, mode, max, self.N)
            
        return simulation_dict

    def generateValueSimulation(self):
        simulation_dict = {}
        for w in self.backlog.work_items:
            [min, mode, max] = w.value_est
            simulation_dict[w] = np.random.default_rng().triangular(min, mode, max, self.N)
            
        return simulation_dict


    # TODO
    def NPV(self, cashflow, rate):
        npv =  npf.npv(rate, cashflow)
        return npv


    def calculate_cashflow(self, s: ReleaseScenario, value_simulation):
        cashflow = []
        #cashflow[0] = sum of value of all work items delivered in period 0
        #cashflow[1] = cashflow[0] + value of workitems delivered in 1
        for release in s:
            sum = 0
            for item in release:
                item_period = s.get_index(release)
                val = value_simulation[item][item_period]
                sum += val
            cashflow.append(sum)
        return cashflow



    # OK
    def punctuality(self, s:ReleaseScenario, p: ReleasePlan):

        nbr_late = 0
        total = p.get_length()
        for w in p.get_work_items():
            if w in s.get_work_items():
                if (s.get_delivery_period(w) > p.get_delivery_period(w)):
                    nbr_late += 1
            if w not in s.get_work_items():
                nbr_late += 1

        punctuality = (total - nbr_late)/total

        return punctuality

    # OK
    def value_cost_ratio(self, p: ReleasePlan, n:int):
        ratio_list = []
        for release in p.releases:
            for w in release:
                val = self.value_simulation[w][n-1]
                cost = self.effort_simulation[w][n-1]
                ratio = val / cost
                ratio_list.append(ratio)

        return ratio_list

    # OK
    def sort_release(self, a: list, b: list):  # a:the list to be sorted, b: ratio_list
        zipped_list = zip(b, a)
        sorted_zipped_list = sorted(zipped_list)
        sorted_list_a = [element for _, element in sorted_zipped_list]
        return sorted_list_a

    # OK
    def generateWorkSequence(self, p: ReleasePlan):
        ws = []
        for period in p:
            for feature in period:
                ws.append(feature)
        return ws


    # helper function 2
    # n: n-th simulation, p:release plan
    def generateReleaseScenario(self, n: int, p: ReleasePlan):
        # sort each release in the release plan
        ratio = self.value_cost_ratio(p, n)
        for release in p:
            release = self.sort_release(release, ratio)

        # ws is a list of p's work items
        ws = self.generateWorkSequence(p)

        s = ReleaseScenario()#check 
        for period in range(len(self.capacity)):
            s.add_release([])
        

        i = 0
        sumCapacity = self.capacity[i]
        sumEffort = 0
        for j in range(len(ws)):
            w = ws[j]
            sumEffort = sumEffort + self.effort_simulation[w][n]
            
            #print(sumEffort, sumCapacity, i)
            while (sumEffort > sumCapacity):
                if(i < len(self.capacity) - 1):
                    i = i + 1
                    sumCapacity = sumCapacity + self.capacity[i]
            
            s.releases[i-1].append(w)
        
        return s

    # OK
    # main function
    def evaluateReleasePlan(self, p: ReleasePlan):
        sumNPV = 0
        sumPunctuality = 0
        for n in range(self.N):
            s = self.generateReleaseScenario(n, p)
            cashflow = self.calculate_cashflow(s, self.value_simulation)
            npv = self.NPV(cashflow, self.r)
            
            sumNPV = sumNPV + npv
            sumPunctuality = sumPunctuality + self.punctuality(s, p)

        return [(sumNPV/self.N), (sumPunctuality/self.N)]


    def npv_distribution(self, p:ReleasePlan):
        npv_list = []
        for n in range(self.N):
            s = self.generateReleaseScenario(n, p)
            cashflow = self.calculate_cashflow(s, self.value_simulation)
            npv = self.NPV(cashflow, self.r)
            npv_list.append(npv)
        return npv_list



