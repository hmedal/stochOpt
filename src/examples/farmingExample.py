'''
Created on Aug 17, 2016

@author: hm568
'''

from gurobipy import *

# Create a new model
farmerModel = Model("Model from pg. 4 of B&L")

# Problem data
yieldValues = {'wheat' : 2.5, 'corn' : 3, 'sugar beets' : 20}
plantingCosts = {'wheat' : 150, 'corn' : 230, 'sugar beets' : 260}
sellingPrices = {'wheat' : 170, 'corn' : 150, 'sugar beets' : 36} # within quota
quotas = {'sugar beets' : 6000}
sellingPricesAboveQuota = {'sugar beets' : 10}
purchasePrices = {'wheat' : 238, 'corn' : 210}
minRequirements = {'wheat' : 200, 'corn' : 240}
totalAvailableLand = 500

# Create variables
cropTypes = ['wheat', 'corn', 'sugar beets']
acresDevotedValues = {}
for cropType in cropTypes:
    acresDevotedValues[cropType] = farmerModel.addVar(vtype=GRB.CONTINUOUS, lb = 0, name="x_" + cropType)
amountsSold = {}
amountsPurchased = {}
for cropType in ['wheat', 'corn']:
    amountsSold[cropType] = farmerModel.addVar(vtype=GRB.CONTINUOUS, lb = 0, name="w_" + cropType)
    amountsPurchased[cropType] = farmerModel.addVar(vtype=GRB.CONTINUOUS, lb = 0, name="y_" + cropType)
amountsSoldAtFavorablePrice = {'sugar beets' : farmerModel.addVar(vtype=GRB.CONTINUOUS, lb = 0, name="w_" + str(3))}
amountsSoldAtLowerPrice = {'sugar beets' : farmerModel.addVar(vtype=GRB.CONTINUOUS, lb = 0, name="w_" + str(4))}

# Integrate new variables
farmerModel.update()

# Set objective
totalPlantingCost = quicksum([plantingCosts[cropType] * acresDevotedValues[cropType] for cropType in cropTypes])
totalPurchaseCost = quicksum([purchasePrices[cropType] * amountsPurchased[cropType] 
                              for cropType in ['wheat', 'corn']])
totalSalesRevenue = quicksum([sellingPrices[cropType] * amountsSold[cropType] 
                            for cropType in ['wheat', 'corn']])
totalSalesRevenue += (sellingPrices['sugar beets'] * amountsSoldAtFavorablePrice['sugar beets'] + 
                      sellingPricesAboveQuota['sugar beets'] * amountsSoldAtLowerPrice['sugar beets'])
farmerModel.setObjective(totalPlantingCost + totalPurchaseCost - totalSalesRevenue, GRB.MINIMIZE)

farmerModel.addConstr(quicksum([acresDevotedValues[cropType] 
                                for cropType in cropTypes]) <= totalAvailableLand)
for cropType in ['wheat', 'corn']:
    farmerModel.addConstr(yieldValues[cropType] * acresDevotedValues[cropType] + 
                          amountsPurchased[cropType] - amountsSold[cropType] >= minRequirements[cropType])
farmerModel.addConstr(amountsSoldAtFavorablePrice['sugar beets'] + amountsSoldAtLowerPrice['sugar beets'] <= 
                      yieldValues['sugar beets'] * acresDevotedValues['sugar beets'])
farmerModel.addConstr(amountsSoldAtFavorablePrice['sugar beets'] <= quotas['sugar beets'])
farmerModel.setParam('OutputFlag', False ) #turn output off
farmerModel.update()

farmerModel.optimize()
for cropType in cropTypes:
    print 'acres of ' + cropType, acresDevotedValues[cropType].x
for cropType in cropTypes:
    print 'yield of ' + cropType, yieldValues[cropType] * acresDevotedValues[cropType].x
for cropType in ['wheat', 'corn']:
    print 'sales of ' + cropType, amountsSold[cropType].x
print 'sales of ' + 'sugar beets', (amountsSoldAtFavorablePrice['sugar beets'].x + 
                                    amountsSoldAtLowerPrice['sugar beets'].x)
print('Overall profit: %g' % -farmerModel.objVal)

yieldValuesInScenarios = {}
for cropType in cropTypes:
    yieldValuesInScenarios[cropType] = {}
    yieldValuesInScenarios[cropType]['good'] =  yieldValues[cropType] * 1.2
    yieldValuesInScenarios[cropType]['fair'] =  yieldValues[cropType]
    yieldValuesInScenarios[cropType]['poor'] =  yieldValues[cropType] * 0.8
    
farmerModels = {}

scenario = 'good'

farmerModels[scenario] = Model("Model from pg. 6 of B&L under " + scenario + " scenario")

# Create variables

acresDevotedValuesForScenario = {}
acresDevotedValuesForScenario[scenario] = {}
for cropType in cropTypes:
    acresDevotedValuesForScenario[scenario][cropType] = farmerModels[scenario].addVar(vtype=GRB.CONTINUOUS, lb = 0, name="x_" + cropType)
amountsSold = {}
amountsPurchased = {}
amountsSold[scenario] = {}
amountsPurchased[scenario] = {}
for cropType in ['wheat', 'corn']:
    amountsSold[scenario][cropType] = farmerModels[scenario].addVar(vtype=GRB.CONTINUOUS, lb = 0, name="w_" + cropType)
    amountsPurchased[scenario][cropType] = farmerModels[scenario].addVar(vtype=GRB.CONTINUOUS, lb = 0, name="y_" + cropType)
amountsSoldAtFavorablePrice = {}
amountsSoldAtFavorablePrice[scenario] = {'sugar beets' : farmerModels[scenario].addVar(vtype=GRB.CONTINUOUS, lb = 0, 
                                                                                name="w_" + str(3))}
amountsSoldAtLowerPrice = {}
amountsSoldAtLowerPrice[scenario] = {'sugar beets' : farmerModels[scenario].addVar(vtype=GRB.CONTINUOUS, lb = 0, name="w_" + str(4))}

# Integrate new variables
farmerModels[scenario].update()

# Set objective
totalPlantingCost = {}
totalPlantingCost[scenario] = quicksum([plantingCosts[cropType] * acresDevotedValuesForScenario[scenario][cropType] for cropType in cropTypes])
totalPurchaseCost = {}
totalPurchaseCost[scenario] = quicksum([purchasePrices[cropType] * amountsPurchased[scenario][cropType] 
                              for cropType in ['wheat', 'corn']])
totalSalesRevenue = {}
totalSalesRevenue[scenario] = quicksum([sellingPrices[cropType] * amountsSold[scenario][cropType] 
                            for cropType in ['wheat', 'corn']])
totalSalesRevenue[scenario] += (sellingPrices['sugar beets'] * amountsSoldAtFavorablePrice[scenario]['sugar beets'] + 
                      sellingPricesAboveQuota['sugar beets'] * amountsSoldAtLowerPrice[scenario]['sugar beets'])
farmerModels[scenario].setObjective(totalPlantingCost[scenario] + totalPurchaseCost[scenario] - totalSalesRevenue[scenario], GRB.MINIMIZE)

farmerModels[scenario].addConstr(quicksum([acresDevotedValuesForScenario[scenario][cropType] 
                                for cropType in cropTypes]) <= totalAvailableLand)
for cropType in ['wheat', 'corn']:
    farmerModels[scenario].addConstr(yieldValuesInScenarios[cropType][scenario] * acresDevotedValuesForScenario[scenario][cropType] + 
                          amountsPurchased[scenario][cropType] - amountsSold[scenario][cropType] >= minRequirements[cropType])
farmerModels[scenario].addConstr(amountsSoldAtFavorablePrice[scenario]['sugar beets'] + 
                                 amountsSoldAtLowerPrice[scenario]['sugar beets'] <= 
                      yieldValuesInScenarios['sugar beets'][scenario] * acresDevotedValuesForScenario[scenario]['sugar beets'])
farmerModels[scenario].addConstr(amountsSoldAtFavorablePrice[scenario]['sugar beets'] <= quotas['sugar beets'])
farmerModels[scenario].setParam('OutputFlag', False ) #turn output off
farmerModels[scenario].update()

farmerModels[scenario].optimize()
for cropType in cropTypes:
    print 'acres of ' + cropType, acresDevotedValuesForScenario[scenario][cropType].x
for cropType in cropTypes:
    print 'yield of ' + cropType, yieldValuesInScenarios[cropType][scenario] * acresDevotedValuesForScenario[scenario][cropType].x
for cropType in ['wheat', 'corn']:
    print 'sales of ' + cropType, amountsSold[scenario][cropType].x
print 'sales of ' + 'sugar beets', (amountsSoldAtFavorablePrice[scenario]['sugar beets'].x + 
                                    amountsSoldAtLowerPrice[scenario]['sugar beets'].x)
print('Overall profit: %g' % -farmerModels[scenario].objVal)

scenario = 'poor'

farmerModels[scenario] = Model("Model from pg. 6 of B&L under " + scenario + " scenario")

# Create variables

acresDevotedValuesForScenario[scenario] = {}
for cropType in cropTypes:
    acresDevotedValuesForScenario[scenario][cropType] = farmerModels[scenario].addVar(vtype=GRB.CONTINUOUS, lb = 0, name="x_" + cropType)
amountsSold[scenario] = {}
amountsPurchased[scenario] = {}
for cropType in ['wheat', 'corn']:
    amountsSold[scenario][cropType] = farmerModels[scenario].addVar(vtype=GRB.CONTINUOUS, lb = 0, name="w_" + cropType)
    amountsPurchased[scenario][cropType] = farmerModels[scenario].addVar(vtype=GRB.CONTINUOUS, lb = 0, name="y_" + cropType)
amountsSoldAtFavorablePrice = {}
amountsSoldAtFavorablePrice[scenario] = {'sugar beets' : farmerModels[scenario].addVar(vtype=GRB.CONTINUOUS, lb = 0, 
                                                                                name="w_" + str(3))}
amountsSoldAtLowerPrice = {}
amountsSoldAtLowerPrice[scenario] = {'sugar beets' : farmerModels[scenario].addVar(vtype=GRB.CONTINUOUS, lb = 0, name="w_" + str(4))}

# Integrate new variables
farmerModels[scenario].update()

# Set objective
totalPlantingCost = {}
totalPlantingCost[scenario] = quicksum([plantingCosts[cropType] * acresDevotedValuesForScenario[scenario][cropType] for cropType in cropTypes])
totalPurchaseCost = {}
totalPurchaseCost[scenario] = quicksum([purchasePrices[cropType] * amountsPurchased[scenario][cropType] 
                              for cropType in ['wheat', 'corn']])
totalSalesRevenue = {}
totalSalesRevenue[scenario] = quicksum([sellingPrices[cropType] * amountsSold[scenario][cropType] 
                            for cropType in ['wheat', 'corn']])
totalSalesRevenue[scenario] += (sellingPrices['sugar beets'] * amountsSoldAtFavorablePrice[scenario]['sugar beets'] + 
                      sellingPricesAboveQuota['sugar beets'] * amountsSoldAtLowerPrice[scenario]['sugar beets'])
farmerModels[scenario].setObjective(totalPlantingCost[scenario] + totalPurchaseCost[scenario] - totalSalesRevenue[scenario], GRB.MINIMIZE)

farmerModels[scenario].addConstr(quicksum([acresDevotedValuesForScenario[scenario][cropType] 
                                for cropType in cropTypes]) <= totalAvailableLand)
for cropType in ['wheat', 'corn']:
    farmerModels[scenario].addConstr(yieldValuesInScenarios[cropType][scenario] * acresDevotedValuesForScenario[scenario][cropType] + 
                          amountsPurchased[scenario][cropType] - amountsSold[scenario][cropType] >= minRequirements[cropType])
farmerModels[scenario].addConstr(amountsSoldAtFavorablePrice[scenario]['sugar beets'] + 
                                 amountsSoldAtLowerPrice[scenario]['sugar beets'] <= 
                      yieldValuesInScenarios['sugar beets'][scenario] * acresDevotedValuesForScenario[scenario]['sugar beets'])
farmerModels[scenario].addConstr(amountsSoldAtFavorablePrice[scenario]['sugar beets'] <= quotas['sugar beets'])
farmerModels[scenario].setParam('OutputFlag', False ) #turn output off
farmerModels[scenario].update()

farmerModels[scenario].optimize()
for cropType in cropTypes:
    print 'acres of ' + cropType, acresDevotedValuesForScenario[scenario][cropType].x
for cropType in cropTypes:
    print 'yield of ' + cropType, yieldValuesInScenarios[cropType][scenario] * acresDevotedValuesForScenario[scenario][cropType].x
for cropType in ['wheat', 'corn']:
    print 'sales of ' + cropType, amountsSold[scenario][cropType].x
print 'sales of ' + 'sugar beets', (amountsSoldAtFavorablePrice[scenario]['sugar beets'].x + 
                                    amountsSoldAtLowerPrice[scenario]['sugar beets'].x)
print('Overall profit: %g' % -farmerModels[scenario].objVal)


farmerModelStochProg = Model("Model from pg. 8 of B&L")
probOfScenario = {'good' : 1/3.0, 'fair' : 1/3.0, 'poor' : 1/3.0}
scenarios = ['good', 'fair', 'poor']
# Create first-stage variables
acresDevotedValuesForSP = {}
for cropType in cropTypes:
    acresDevotedValuesForSP[cropType] = farmerModelStochProg.addVar(vtype=GRB.CONTINUOUS, lb = 0, name="x_" + cropType)
# Create second-stage variables
for scenario in scenarios:
    amountsSold[scenario] = {}
    amountsPurchased[scenario] = {}
    for cropType in ['wheat', 'corn']:
        amountsSold[scenario][cropType] = farmerModelStochProg.addVar(vtype=GRB.CONTINUOUS, lb = 0, name="w_" + cropType)
        amountsPurchased[scenario][cropType] = farmerModelStochProg.addVar(vtype=GRB.CONTINUOUS, lb = 0, name="y_" + cropType)
    amountsSoldAtFavorablePrice[scenario] = {'sugar beets' : farmerModelStochProg.addVar(vtype=GRB.CONTINUOUS, lb = 0, 
                                                                                    name="w_" + str(3))}
    amountsSoldAtLowerPrice[scenario] = {'sugar beets' : farmerModelStochProg.addVar(vtype=GRB.CONTINUOUS, lb = 0, name="w_" + str(4))}

# Integrate new variables
farmerModelStochProg.update()

# Set objective
for scenario in scenarios:
    totalPlantingCost[scenario] = quicksum([plantingCosts[cropType] * acresDevotedValuesForSP[cropType] for cropType in cropTypes])
    totalPurchaseCost[scenario] = quicksum([purchasePrices[cropType] * amountsPurchased[scenario][cropType] 
                                  for cropType in ['wheat', 'corn']])
    totalSalesRevenue[scenario] = quicksum([sellingPrices[cropType] * amountsSold[scenario][cropType] 
                                for cropType in ['wheat', 'corn']])
    totalSalesRevenue[scenario] += (sellingPrices['sugar beets'] * amountsSoldAtFavorablePrice[scenario]['sugar beets'] + 
                          sellingPricesAboveQuota['sugar beets'] * amountsSoldAtLowerPrice[scenario]['sugar beets'])
totalExpectedCost = quicksum([probOfScenario[scenario] * (totalPlantingCost[scenario] + totalPurchaseCost[scenario] - totalSalesRevenue[scenario]) for scenario in scenarios])
farmerModelStochProg.setObjective(totalExpectedCost, GRB.MINIMIZE)

# first-stage constraints
farmerModelStochProg.addConstr(quicksum([acresDevotedValuesForSP[cropType] 
                                    for cropType in cropTypes]) <= totalAvailableLand)
# second-stage constraints
for scenario in scenarios:
    for cropType in ['wheat', 'corn']:
        farmerModelStochProg.addConstr(yieldValuesInScenarios[cropType][scenario] * acresDevotedValuesForSP[cropType] + 
                              amountsPurchased[scenario][cropType] - amountsSold[scenario][cropType] >= minRequirements[cropType])
    farmerModelStochProg.addConstr(amountsSoldAtFavorablePrice[scenario]['sugar beets'] + 
                                     amountsSoldAtLowerPrice[scenario]['sugar beets'] <= 
                          yieldValuesInScenarios['sugar beets'][scenario] * acresDevotedValuesForSP['sugar beets'])
    farmerModelStochProg.addConstr(amountsSoldAtFavorablePrice[scenario]['sugar beets'] <= quotas['sugar beets'])
farmerModelStochProg.setParam('OutputFlag', False ) #turn output off
farmerModelStochProg.update()
farmerModelStochProg.optimize()
print 'first stage decisions'
for cropType in cropTypes:
        print 'acres of ' + cropType, acresDevotedValuesForSP[cropType].x
for scenario in scenarios:
    print 'scenario:', scenario
    for cropType in cropTypes:
        print 'yield of ' + cropType, yieldValuesInScenarios[cropType][scenario] * acresDevotedValuesForSP[cropType].x
    for cropType in ['wheat', 'corn']:
        print 'sales of ' + cropType, amountsSold[scenario][cropType].x
    print 'sales of ' + 'sugar beets', (amountsSoldAtFavorablePrice[scenario]['sugar beets'].x + 
                                        amountsSoldAtLowerPrice[scenario]['sugar beets'].x)
print('Overall expected profit: $%g' % -farmerModelStochProg.objVal)