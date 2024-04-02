# Safety Aware Reasoning Project

## TODOs

Consequence state space
- [ ] input consequence state space
- [ ] error check consequence state space
- [ ] update policy/utility info with state space
- [ ] make sure everything in code is named appropriately
- [ ] ask user for input on state space
- [ ] add querying state space info to red team data extension

Counter-factual red teaming
- [ ] rename red teamed data files to indicate both RS generation and CFA generation
- [ ] add support to red team node to do both RS and CFA modes
- [ ] randomly select risky scenario
- [ ] randomly select risk mitigating action
- [ ] ask user for input on state space
- [ ] error checking on user input
- [ ] check for multiples? may not be necessary
- [ ] write to YAML file

Model creation
- [ ] input risky conditions for real (not just tests for development purposes)
- [ ] input action spaces for real (not just tests for development purposes)
- [ ] input initial policy starters for real (not just tests for development purposes)
- [ ] generate red teamed data (~500 data points per robot per environment)
- [ ] logistic regression analysis (combined, CLR only, Val only, household only, lunar only, CLR/household, CLR/lunar, Val/household, Val/lunar)
- [ ] model(s) training and validation
- [ ] save models for later use

Safety score and risk score computations
- [ ] estimate safety/risk of current plan/task
- [ ] relevant for reporting

Online data point recording
- [ ] record data points online during task execution, store in separate dataset
- [ ] relearn from dataset and/or suggestions to relearn from dataset when new data is collected

Counterfactual reasoning for identifying upstream decision points
- [ ] report actions to user
- [ ] ask user for input on what action should have been taken
- [ ] generate additional data points based on user input
- [ ] add to online dataset
