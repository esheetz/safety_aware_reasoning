# Safety Aware Reasoning Project

## TODOs

Model creation
- [ ] input risky conditions for real (not just tests for development purposes)
- [ ] input action spaces for real (not just tests for development purposes)
- [ ] input initial policy starters for real (not just tests for development purposes)
- [ ] input consequence states for real (not just tests for development purposes)
- [ ] final testing of data generation; do I need to add checks for repeated scenario generation?
- [ ] generate red teamed data (~500 data points per robot per environment) (depending on how long this takes, may put off CLR for later)
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
