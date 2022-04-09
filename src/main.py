from platform import release
import numpy
import pandas as pd
from release_plan import ReleasePlan
from backlog import Backlog
from work_item import WorkItem
from simulator import ReleasePlanSimulator
#install openpyxl
import seaborn as sns
import matplotlib.pyplot as plt


#read file
file = pd.ExcelFile('./src/Council-Backlog-Raw.xlsx')
df_parameters = pd.read_excel(file,sheet_name='Planning Parameters')
df_backlog = pd.read_excel(file,sheet_name='Backlog & dependencies')
df_effort = pd.read_excel(file, sheet_name='Effort Estimates')
df_value = pd.read_excel(file, sheet_name='Value Estimates')

#read parameters
planning_horizon = df_parameters['Planning Horizon'][0]
capacity_one = df_parameters['Capacity (man-hours)'][0]
capacity = planning_horizon * [int(capacity_one)]

investment_horizon = df_parameters['Investment Horizon'][0]
discount_rate = df_parameters['Discount rate'][0]
budget = df_parameters['Budget (£1,000)'][0]

#backlog work items
backlog = Backlog()
name_list = []
for name in df_backlog['Work Items']:
    name_list.append(name)

work_item_list = []
max_iter = len(df_effort['Work Items'])
i = 0
for i in range(max_iter):
    label = df_effort['Work Items'][i]
    effort_low = df_effort['Lower Quartile'][i]
    effort_med = df_effort['Median'][i]
    effort_high = df_effort['Upper Quartile'][i]
    effort_est = [effort_low, effort_med, effort_high]

    value_low = df_value['Lower Quartile'][i]
    value_med = df_value['Median'][i]
    value_high = df_value['Upper Quartile'][i]
    value_est = [value_low, value_med, value_high]

    if label in name_list:
        if (effort_est != [0,0,0] and value_est != [0,0,0]):
            w = WorkItem(label)
            w.add_effort_est(effort_low, effort_med, effort_high)
            w.add_value_est(value_low, value_med, value_high)
            work_item_list.append(w)

    i += 1

backlog.add_work_items(work_item_list)

    
#Release Plan
df_plan = pd.read_excel('./src/Council-Backlog-Plan.xlsx')
release_plan = ReleasePlan()
period_list = ['Period 0', 'Period 1', 'Period 2']
for i in period_list:
    item_list = []
    for item in df_plan[i]:
        for w in backlog.work_items:
            if (item == w.label):
                item_list.append(w)
    release_plan.add_release(item_list)


sim = ReleasePlanSimulator(backlog, H=planning_horizon, capacity=capacity,L=investment_horizon, r=discount_rate,B=budget,N=10000)
e = sim.evaluateReleasePlan(release_plan)

#npv = sim.npv_distribution(release_plan)
#lt.hist(npv)
#plt.show()
print(e)