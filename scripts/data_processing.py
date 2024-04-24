#!/usr/bin/env python3
"""
Data Processing Helper Classes
Emily Sheetz, NSTGRO VTE 2024
"""

import rospy

import os, yaml
import pandas as pd

# data readers
from risky_condition_reader import RiskyConditionReader
from consequence_state_reader import ConsequenceStateReader
from risk_mitigating_action_reader import RiskMitigatingActionReader
from risk_mitigating_policy_data_reader import RiskMitigatingPolicyDataReader

##########################
### DATASET INFO CLASS ###
##########################

class DatasetInfo:
    """
    Stores information and variables related to safety-aware reasoning datasets
    """

    def __init__(self):
        self.initialize_files_directories()
        self.initialize_action_space_encodings()

    ######################
    ### INITIALIZATION ###
    ######################

    def initialize_files_directories(self):
        # get path of this script
        script_path = os.path.abspath(os.path.dirname( __file__ ))
        
        # data directory
        self.data_dir = script_path + "/../data/"

        # supported robots/environments
        self.supported_robots = ['clr','val','val_clr']
        self.supported_envs = ['household','lunar_habitat']

        # random risky scenario
        self.rrs_policy_file_name = "red_teamed_risk_mitigating_policy_data.yaml"
        self.rrs_dataset_file_name = "risky_scenario_policy_data.csv"
        # counter-factual action
        self.cfa_policy_file_name = "counter_factual_policy_data.yaml"
        self.cfa_dataset_file_name = "counter_factual_policy_data.csv"

        # pre-processed data name
        self.data_file_name = "risk_mitigating_action_utility_data.csv"

        # saved models directory
        self.models_dir = script_path + "/../saved_models/"

        # models file ending
        self.model_file_end = "_model.sav"

        return

    def initialize_action_space_encodings(self):
        # initialize dictionary of encodings
        self.action_space_encodings = {}

        # loop through robot/environment combinations
        for r in self.supported_robots:
            for e in self.supported_envs:
                # initialize dictionary
                key = self.create_action_encoding_dictionary_key(r, e)
                self.action_space_encodings[key] = {}

                # set dictionary
                self.action_space_encodings[key] = self.get_action_encoding_for_robot_env(r, e)

        return

    #########################
    ### GETTERS / SETTERS ###
    #########################

    def get_rrs_policy_full_path(self, robot):
        return self.data_dir + robot + "/" + self.rrs_policy_file_name

    def get_rrs_dataset_full_path(self, robot, env):
        path = self.data_dir + robot + "/" + env + "/"
        file_name = path + self.rrs_dataset_file_name
        return path, file_name

    def get_cfa_policy_full_path(self, robot):
        return self.data_dir + robot + "/" + self.cfa_policy_file_name

    def get_cfa_dataset_full_path(self, robot, env):
        path = self.data_dir + robot + "/" + env + "/"
        file_name = path + self.cfa_dataset_file_name
        return path, file_name

    def get_combined_dataset_full_path(self, robot, env):
        path = self.data_dir + robot + "/" + env + "/"
        file_name = path + self.data_file_name
        return path, file_name

    def get_action_encoding_for_robot_env(self, robot, env):
        # create reader and process data
        action_space_reader = RiskMitigatingActionReader(robot=robot, environment=env)
        action_space_reader.process_risk_mitigating_actions()

        # get action space names
        action_names = action_space_reader.get_risk_mitigating_action_names()
        
        # initialize dictionary
        action_space_encodings = {}

        # add action encodings to dictionary
        for i, item in enumerate(action_names):
            action_space_encodings[item] = i

        return action_space_encodings

    def get_action_autonomy_space_for_robot_env(self, robot, env):
        # create reader and process data
        action_space_reader = RiskMitigatingActionReader(robot=robot, environment=env)
        action_space_reader.process_risk_mitigating_actions()

        # initialize dictionary
        action_autonomy_space = {}

        # add action and autonomy level to dictionary
        for action in action_space_reader.get_risk_mitigating_actions():
            a_name = action.get_action_name()
            a_level = action.get_action_autonomy_level()
            # add entry to dictionary
            action_autonomy_space[a_name] = a_level

        return action_autonomy_space

    def get_consequence_space_for_robot_env(self, robot, env):
        # create reader and process data
        conseq_space_reader = ConsequenceStateReader(robot=robot, environment=env)
        conseq_space_reader.process_consequence_states()

        # initialize list
        conseq_space = []

        # add consequence name to list
        for conseq in conseq_space_reader.get_consequence_states():
            c_name = conseq.get_consequence_name()
            conseq_space.append(c_name)

        return conseq_space

    def get_risky_conditions_for_robot_env(self, robot, env):
        # create reader and process data
        state_space_reader = RiskyConditionReader(robot=robot, environment=env)
        state_space_reader.process_risky_conditions()

        # initialize dictionary
        state_space = {}

        # add risky condition information to dictionary
        for cond in state_space_reader.get_risky_conditions():
            c_name = cond.get_condition_name()
            c_likeli = cond.get_likelihood_level()
            c_conseq = cond.get_consequence_class()
            c_risk = cond.get_matrix_risk_score()
            c_safety = cond.get_matrix_safety_score()
            # add each entry to dictionary
            state_space[c_name] = {}
            state_space[c_name]['likelihood'] = c_likeli
            state_space[c_name]['consequence'] = c_conseq
            state_space[c_name]['risk'] = c_risk
            state_space[c_name]['safety'] = c_safety

        return state_space

    ###############
    ### HELPERS ###
    ###############

    def create_action_encoding_dictionary_key(self, robot, env):
        key = robot + "_" + env
        return key



################################
### DATASET FORMATTING CLASS ###
################################

class DatasetColumns:
    """
    Stores formatting and column information about the dataset
    """

    def __init__(self, robot="val_clr", environment="lunar_habitat"):
        # set internal paramters
        self.robot_name = robot
        self.environment_name = environment

        # initialize data info
        self.info = DatasetInfo()

        # initialize relevant information
        self.action_encoding = self.info.get_action_encoding_for_robot_env(self.robot_name, self.environment_name)
        self.action_autonomy_space = self.info.get_action_autonomy_space_for_robot_env(self.robot_name, self.environment_name)
        self.consequence_space = self.info.get_consequence_space_for_robot_env(self.robot_name, self.environment_name)
        self.risky_conditions = self.info.get_risky_conditions_for_robot_env(self.robot_name, self.environment_name)

        # initialize column names and types
        self.initialize_column_names_types()

    ######################
    ### INITIALIZATION ###
    ######################

    def initialize_column_names_types(self):
        self.column_names = []
        self.column_types = {}

        # add column names for risky conditions
        for cond in self.risky_conditions.keys():
            col_name = self.get_col_name_for_condition(cond)
            self.column_names.append(col_name)
            self.column_types[col_name] = int
            col_name = self.get_col_name_for_condition_risk(cond)
            self.column_names.append(col_name)
            self.column_types[col_name] = float
            col_name = self.get_col_name_for_condition_safety(cond)
            self.column_names.append(col_name)
            self.column_types[col_name] = float

        # add column names for consequences pre-action
        for conseq in self.consequence_space:
            col_name = self.get_col_name_for_consequence(conseq, pre_action=True)
            self.column_names.append(col_name)
            self.column_types[col_name] = int

        # add columns for risk/safety of whole state
        col_name = self.get_col_name_for_state_risk()
        self.column_names.append(col_name)
        self.column_types[col_name] = float
        col_name = self.get_col_name_for_state_safety()
        self.column_names.append(col_name)
        self.column_types[col_name] = float

        # add column names for consequences post-action
        for conseq in self.consequence_space:
            col_name = self.get_col_name_for_consequence(conseq, pre_action=False)
            self.column_names.append(col_name)
            self.column_types[col_name] = int

        # add columns for action and encoded action
        col_name = self.get_col_name_for_action()
        self.column_names.append(col_name)
        self.column_types[col_name] = str
        col_name = self.get_col_name_for_action_encoded()
        self.column_names.append(col_name)
        self.column_types[col_name] = int

        return

    ###########################
    ### COLUMN NAME HELPERS ###
    ###########################

    def get_col_name_for_condition(self, cond_name):
        return "COND_NAME_" + cond_name

    def get_col_name_for_condition_risk(self, cond_name):
        return "COND_RISK_" + cond_name

    def get_col_name_for_condition_safety(self, cond_name):
        return "COND_SAFETY_" + cond_name

    def get_col_name_for_consequence(self, conseq_name, pre_action=True):
        if pre_action:
            return "CONSEQ_PRE_ACT_" + conseq_name
        else:
            return "CONSEQ_POST_ACT_" + conseq_name

    def get_col_name_for_state_risk(self):
        return "STATE_RISK"

    def get_col_name_for_state_safety(self):
        return "STATE_SAFETY"

    def get_col_name_for_action(self):
        return "RISK_MITIGATING_ACTION"

    def get_col_name_for_action_encoded(self):
        return "RISK_MITIGATING_ACTION_ENCODED"

    def check_col_name_for_condition(self, col_name):
        return "COND_NAME_" in col_name

    def check_col_name_for_condition_risk(self, col_name):
        return "COND_RISK_" in col_name

    def check_col_name_for_condition_safety(self, col_name):
        return "COND_SAFETY_" in col_name

    def check_col_name_for_consequence(self, col_name, pre_action=True):
        if pre_action:
            return "CONSEQ_PRE_ACT_" in col_name
        else:
            return "CONSEQ_POST_ACT_" in col_name

    def check_col_name_for_state_risk(self, col_name):
        return "STATE_RISK" == col_name

    def check_col_name_for_state_safety(self, col_name):
        return "STATE_SAFETY" == col_name

    def check_col_name_for_action(self, col_name):
        return "RISK_MITIGATING_ACTION" == col_name

    def check_col_name_for_action_encoded(self, col_name):
        return "RISK_MITIGATING_ACTION_ENCODED" == col_name

    def get_condition_name_from_col_name(self, col_name):
        return col_name.replace("COND_NAME_","").replace("COND_RISK_","").replace("COND_SAFETY_","")

    def get_consequence_name_from_col_name(self, col_name):
        return col_name.replace("CONSEQ_PRE_ACT_","").replace("CONSEQ_POST_ACT_","")



################################
### DATA PREPROCESSING CLASS ###
################################

class DataPreprocessing:
    """
    Pre-processes red teamed data (YAML files) into CSV files
    """

    def __init__(self, robot="val_clr", environment="lunar_habitat"):
        # set internal paramters
        self.robot_name = robot
        self.environment_name = environment

        # initialize data info
        self.info = DatasetInfo()

        # initialize data formatting
        self.col_info = DatasetColumns(self.robot_name, self.environment_name)

        # initialize relevant information
        self.action_encoding = self.info.get_action_encoding_for_robot_env(self.robot_name, self.environment_name)
        self.action_autonomy_space = self.info.get_action_autonomy_space_for_robot_env(self.robot_name, self.environment_name)
        self.consequence_space = self.info.get_consequence_space_for_robot_env(self.robot_name, self.environment_name)
        self.risky_conditions = self.info.get_risky_conditions_for_robot_env(self.robot_name, self.environment_name)

    ######################
    ### CREATE DATASET ###
    ######################

    def convert_yamls_to_dataset_csv(self):
        df_rrs = self.convert_rrs_yaml_to_dataset_csv()
        df_cfa = self.convert_cfa_yaml_to_dataset_csv()
        df = self.create_combined_csv(df_rrs, df_cfa)
        return

    def convert_rrs_yaml_to_dataset_csv(self):
        # create data frame
        df_rrs = self.convert_yaml_to_pandas(self.info.get_rrs_policy_full_path(self.robot_name))

        # save data frame to file
        path, file_name = self.info.get_rrs_dataset_full_path(self.robot_name, self.environment_name)
        self.save_pandas_as_csv(df_rrs, path, file_name)

        return df_rrs

    def convert_cfa_yaml_to_dataset_csv(self):
        # create data frame
        df_cfa = self.convert_yaml_to_pandas(self.info.get_cfa_policy_full_path(self.robot_name))

        # save data frame to file
        path, file_name = self.info.get_cfa_dataset_full_path(self.robot_name, self.environment_name)
        self.save_pandas_as_csv(df_cfa, path, file_name)

        return df_cfa

    def create_combined_csv(self, df1, df2):
        # create combined data frame
        df = pd.concat([df1, df2], ignore_index=True)

        # save data frame to file
        path, file_name = self.info.get_combined_dataset_full_path(self.robot_name, self.environment_name)
        self.save_pandas_as_csv(df, path, file_name)

        return df

    def save_pandas_as_csv(self, df, csv_path, csv_file):
        # check if path exists:
        if not os.path.exists(csv_path):
            # create directory
            os.mkdir(csv_path)

        # save data frame to csv file
        df.to_csv(csv_file, index=False) # encoding='utf-8'
        return

    def convert_yaml_to_pandas(self, yaml_file):
        # open yaml file
        fo = open(yaml_file)
        yaml_dict = yaml.load(fo, Loader=yaml.FullLoader)
        fo.close()

        # get policy data
        policy_data = yaml_dict[self.environment_name]['policy_data']

        # initialize dictionary with column names as keys
        dataset_dict = {}
        for col_name in self.col_info.column_names:
            dataset_dict[col_name] = []

        # compute column indices that include condition risks
        cond_risk_cols = [name for name in self.col_info.column_names if self.col_info.check_col_name_for_condition_risk(name)]
        # cond_risk_col_idxs = [i for i,name in enumerate(self.col_info.column_names) if self.col_info.check_col_name_for_condition_risk(name)]

        # look through list of policy data points
        for pol_point in policy_data:
            # set data for each column
            for col_name in self.col_info.column_names:
                # get column type
                col_type = self.col_info.column_types[col_name]

                # set data for this column
                if self.col_info.check_col_name_for_condition(col_name):
                    # get condition name from current column
                    cond_name = self.col_info.get_condition_name_from_col_name(col_name)
                    # check if condition is present in policy data point
                    if cond_name in pol_point['conditions']:
                        # condition is present in this data point, set to True
                        dataset_dict[col_name].append( col_type(1) )
                    else:
                        # condition is not present in this data point, set to False
                        dataset_dict[col_name].append( col_type(0) )
                elif self.col_info.check_col_name_for_condition_risk(col_name):
                    # get condition name from current column
                    cond_name = self.col_info.get_condition_name_from_col_name(col_name)
                    # check if condition is present in policy data point
                    if cond_name in pol_point['conditions']:
                        # condition is present in this data point, set risk
                        dataset_dict[col_name].append( col_type(self.risky_conditions[cond_name]['risk']) )
                    else:
                        # condition is not present in this data point, set risk to 0
                        dataset_dict[col_name].append( col_type(0.0) )
                elif self.col_info.check_col_name_for_condition_safety(col_name):
                    # get condition name from current column
                    cond_name = self.col_info.get_condition_name_from_col_name(col_name)
                    # check if condition is present in policy data point
                    if cond_name in pol_point['conditions']:
                        # condition is present in this data point, set safety
                        dataset_dict[col_name].append( col_type(self.risky_conditions[cond_name]['safety']) )
                    else:
                        # condition is not present in this data point, set safety to 1
                        dataset_dict[col_name].append( col_type(1.0) )
                elif self.col_info.check_col_name_for_consequence(col_name, pre_action=True):
                    # get consequence name from current column
                    conseq_name = self.col_info.get_consequence_name_from_col_name(col_name)
                    # check if consequence is present in policy data point
                    if conseq_name in pol_point['consequences_before_action']:
                        # consequence is present in this data point, set to True
                        dataset_dict[col_name].append( col_type(1) )
                    else:
                        # consequence is not present in this data point, set to False
                        dataset_dict[col_name].append( col_type(0) )
                elif self.col_info.check_col_name_for_consequence(col_name, pre_action=False):
                    # get consequence name from current column
                    conseq_name = self.col_info.get_consequence_name_from_col_name(col_name)
                    # check if consequence is present in policy data point
                    if conseq_name in pol_point['consequences_after_action']:
                        # consequence is present in this data point, set to True
                        dataset_dict[col_name].append( col_type(1) )
                    else:
                        # consequence is not present in this data point, set to False
                        dataset_dict[col_name].append( col_type(0) )
                elif self.col_info.check_col_name_for_state_risk(col_name):
                    # get risks from all conditions
                    risks = [dataset_dict[col][-1] for col in cond_risk_cols]
                    # state risk is maximum of all risks
                    dataset_dict[col_name].append( col_type(max(risks)) )
                elif self.col_info.check_col_name_for_state_safety(col_name):
                    # get state risk
                    risk = dataset_dict[self.col_info.get_col_name_for_state_risk()][-1]
                    # state safety is 1 - state risk
                    dataset_dict[col_name].append( col_type(1 - risk) )
                elif self.col_info.check_col_name_for_action(col_name):
                    # set action name
                    dataset_dict[col_name].append( col_type(pol_point['action']) )
                elif self.col_info.check_col_name_for_action_encoded(col_name):
                    # set encoded action name
                    dataset_dict[col_name].append( col_type(self.action_encoding[pol_point['action']]) )
                else:
                    # should never happen
                    continue
            # end processing column name
        # end processing data points

        # create data frame from dictionary
        df = pd.DataFrame(dataset_dict)

        return df



#############################
### DATA PROCESSING CLASS ###
#############################

class DataProcessing:
    """
    Process red teamed data
    """

    def __init__(self, robot="val_clr", environment="lunar_habitat"):
        # set internal paramters
        self.robot_name = robot
        self.environment_name = environment

        # initialize data info
        self.info = DatasetInfo()

        # initialize data formatting
        self.col_info = DatasetColumns(self.robot_name, self.environment_name)

        # initialize data frame
        self.initialize_data_frame()

    ######################
    ### INITIALIZATION ###
    ######################

    def initialize_data_frame(self):
        # get file name
        _, self.data_file_name = self.info.get_combined_dataset_full_path(self.robot_name, self.environment_name)

        # create data frame
        self.df = pd.read_csv(self.data_file_name)

    ################
    ### PRINTING ###
    ################

    def print_summary_info(self):
        print("*** COLUMN NAMES:")
        print(self.df.columns)
        print("*** INFO:")
        print(self.df.info)
        print("*** SHAPE:")
        print(self.df.shape)
        print("*** HEAD:")
        print(self.df.head())
        return



#####################
### MAIN FUNCTION ###
#####################

if __name__ == '__main__':
    # set node name
    node_name = "SARDataProcessingNode"
    param_prefix = "/" + node_name + "/"

    # get ROS parameters
    robot_name = rospy.get_param(param_prefix + 'robot', "all")
    env_name = rospy.get_param(param_prefix + 'environment', "all")

    # initialize node
    rospy.init_node(node_name)

    rospy.loginfo("[SAR Data Processing Node] Starting to process all data!")

    # create data info
    info = DatasetInfo()

    # initialize robots and envs to be processed
    robots = []
    envs = []

    # check robot and env inputs
    if robot_name == "all":
        robots = info.supported_robots
    elif robot_name in info.supported_robots:
        robots = [robot_name]
    else:
        rospy.logwarn("[SAR Data Processing Node] Unrecognized robot %s, defaulting to 'all'", robot_name)
        robots = info.supported_robots

    if env_name == "all":
        envs = info.supported_envs
    elif env_name in info.supported_envs:
        envs = [env_name]
    else:
        rospy.logwarn("[SAR Data Processing Node] Unrecognized environment %e, defaulting to 'all'", env_name)

    # process all data
    for robot in robots:
        for env in envs:
            # create data pre-processing object
            data_preprocess = DataPreprocessing(robot, env)

            # create dataset csvs
            rospy.loginfo("[SAR Data Processing Node] Processing data for robot %s in %s environment",
                          robot.upper(), env.upper())
            data_preprocess.convert_yamls_to_dataset_csv()
            rospy.loginfo("[SAR Data Processing Node] Created datasets for robot %s in %s environment",
                          robot.upper(), env.upper())

    rospy.loginfo("[SAR Data Processing Node] Completed data processing!")

    rospy.loginfo("[SAR Data Processing Node] Node stopped, all done!")
