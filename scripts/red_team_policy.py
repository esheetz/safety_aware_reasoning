#!/usr/bin/env python3
"""
Red Team Policy Class
Emily Sheetz, NSTGRO VTE 2024
"""

import rospy

import os, shutil
from copy import deepcopy
import yaml

from yaml_formatting_checks import YAMLChecks
from yaml_formatting_checks import YAMLPolicyDataChecks as YAMLPolicy

# import state space, action space, and policy data point classes
from risky_condition import RiskyCondition
from risk_mitigating_action import RiskMitigatingAction
from risk_mitigating_policy_data_point import RiskMitigatingPolicyDataPoint

# import state space, action space, and policy data readers
from risky_condition_reader import RiskyConditionReader
from risk_mitigating_action_reader import RiskMitigatingActionReader
from risk_mitigating_policy_data_reader import RiskMitigatingPolicyDataReader

class RedTeamPolicy:
    def __init__(self, robot="val", environment="lunar_habitat"):
        # set internal parameters
        self.robot_name = robot
        self.environment_name = environment

        # initialize readers
        self.state_space_reader = RiskyConditionReader(robot=self.robot_name,
                                                       environment=self.environment_name)
        self.action_space_reader = RiskMitigatingActionReader(robot=self.robot_name,
                                                              environment=self.environment_name)
        self.policy_starter_reader = RiskMitigatingPolicyDataReader(robot=self.robot_name,
                                                                    environment=self.environment_name,
                                                                    human_gen_data=True)
        self.red_team_policy_reader = RiskMitigatingPolicyDataReader(robot=self.robot_name,
                                                                     environment=self.environment_name,
                                                                     human_gen_data=False)

        # set red teamed data file path
        self.red_team_data_full_path = self.red_team_policy_reader.get_risk_mitigating_policy_data_file_path()

        # initialize dictionary for policy data
        self.policy_data = {}

        # initialize flags
        self.valid_policy = False
        self.initialized = False

    #######################
    ### GETTERS/SETTERS ###
    #######################

    def get_robot_name(self):
        return self.robot_name

    def get_environment_name(self):
        return self.environment_name

    def get_state_space(self):
        return self.state_space_reader.get_risky_condition_names()

    def get_risky_condition_with_name(self, condition_name):
        return self.state_space_reader.get_risky_condition_with_name(condition_name)

    def get_action_space(self):
        return self.action_space_reader.get_risk_mitigating_action_names()

    def get_risk_mitigating_action_with_name(self, action_name):
        return self.action_space_reader.get_risk_mitigating_action_with_name(action_name)

    def get_red_team_data_file_path(self):
        return self.red_team_data_full_path

    def get_red_team_policy_data(self):
        return self.policy_data

    def get_num_red_team_policy_data(self):
        return len(self.policy_data.keys())

    ######################
    ### INITIALIZATION ###
    ######################

    def initialize(self):
        # initialize flag
        self.initialized = True

        # initialize spaces
        self.__initialize_state_space()
        self.__initialize_action_space()
        self.__initialize_policies()        

        # error check policies against state and action spaces
        valid_policies = self.__check_policies_against_state_action_spaces()

        # make sure human-generated policy data is in red teamed policy
        if valid_policies:
            self.policy_data = deepcopy(self.red_team_policy_reader.get_risk_mitigating_policy_data())
            self.valid_policy = self.__red_team_policy_includes_human_policy()

        return

    ##########################
    ### UPDATE POLICY DATA ###
    ##########################

    def update_policy(self, policy_data_point):
        # add data point to policy
        self.policy_data[policy_data_point.get_policy_data_point_condition_names()] = policy_data_point
        return

    #################################
    ### WRITE POLICY DATA TO FILE ###
    #################################

    def write_policy_to_file(self):
        # format policy data as YAML list
        yaml_policy_list = YAMLPolicy.format_policy_as_yaml_list(self.policy_data)

        # open YAML file in read mode and load dict
        fo = open(self.red_team_data_full_path, 'r')
        yaml_dict = yaml.load(fo, Loader=yaml.FullLoader)
        fo.close()

        # modify dictionary with policy data
        yaml_dict[self.environment_name]['policy_data'] = yaml_policy_list

        # open YAML file in write mode and dump dict
        fo = open(self.red_team_data_full_path, 'w')
        yaml.dump(yaml_dict, fo, default_flow_style=False, sort_keys=False)
        fo.close()

        return

    #######################################
    ### INITIALIZATION HELPER FUNCTIONS ###
    #######################################

    def __initialize_state_space(self):
        # process state space
        self.state_space_reader.process_risky_conditions()
        if not self.state_space_reader.check_valid_conditions():
            rospy.logerr("[Red Team Data Extension] Could not initialize state space")
            self.initialized = False
        else:
            rospy.loginfo("[Red Team Data Extension] Successfully initialized state space!")
        return

    def __initialize_action_space(self):
        # process action space
        self.action_space_reader.process_risk_mitigating_actions()
        if not self.action_space_reader.check_valid_actions():
            rospy.logerr("[Red Team Data Extension] Could not initialize action space")
            self.initialized = False
        else:
            rospy.loginfo("[Red Team Data Extension] Successfully initialized action space!")
        return

    def __initialize_policies(self):
        self.__initialize_human_generated_policy()
        self.__initialize_red_team_generated_policy()
        return

    def __initialize_human_generated_policy(self):
        # process policy data
        self.policy_starter_reader.process_risk_mitigating_policy_data()
        if not self.policy_starter_reader.check_valid_policy():
            rospy.logerr("[Red Team Data Extension] Could not initialize human-generated policy data points")
            rospy.logwarn("[Red Team Data Extension] Skipping initialization of red team generated policy data points")
            self.initialized = False
        else:
            rospy.loginfo("[Red Team Data Extension] Successfully initialized human-generated policy data points!")
        return

    def __initialize_red_team_generated_policy(self):
        # process red team policy data only if policy starter processed correctly
        if self.policy_starter_reader.check_valid_policy():
            # check if red team policy data exists and is non-empty
            red_team_exists = YAMLChecks.check_yaml_existence(self.red_team_policy_reader.get_risk_mitigating_policy_data_file_path())
            # check if red team policy data is non-empty
            red_team_nonempty = YAMLChecks.check_yaml_nonempty(self.red_team_policy_reader.get_risk_mitigating_policy_data_file_path())
            # check if red team needs to be initialized
            if not (red_team_exists and red_team_nonempty):
                rospy.loginfo("[Red Team Data Extension] Initializing red team generated policy data from human-generated policy data...")
                # red team data does not exist or is empty, so copy from human-generated data
                shutil.copyfile(src=self.policy_starter_reader.get_risk_mitigating_policy_data_file_path(),
                                dst=self.red_team_policy_reader.get_risk_mitigating_policy_data_file_path())

            # process red team policy data
            self.red_team_policy_reader.process_risk_mitigating_policy_data()
            if not self.red_team_policy_reader.check_valid_policy():
                rospy.logerr("[Red Team Data Extension] Could not initialize red team generated policy data points")
                self.initialized = False
            else:
                rospy.loginfo("[Red Team Data Extension] Successfully initialized red team generated policy data points!")

        return

    def __check_policies_against_state_action_spaces(self):
        # get names of conditions and actions
        state_space_names = self.state_space_reader.get_risky_condition_names()
        action_space_names = self.action_space_reader.get_risk_mitigating_action_names()

        # check human-generated policy
        valid_human_gen_policy = self.__check_policy_against_state_action_spaces("human-generated",
                                                                                   self.policy_starter_reader.get_risk_mitigating_policy_data(),
                                                                                   state_space_names,
                                                                                   action_space_names)
        # check red team policy
        valid_red_team_policy = self.__check_policy_against_state_action_spaces("red team generated",
                                                                                   self.red_team_policy_reader.get_risk_mitigating_policy_data(),
                                                                                   state_space_names,
                                                                                   action_space_names)

        # check valid policies
        valid_policies = valid_human_gen_policy and valid_red_team_policy
        if not valid_policies:
            rospy.logerr("[Red Team Data Extension] Invalid policies do not match state and action spaces")
            self.initialized = False
        else:
            rospy.loginfo("[Red Team Data Extension] Policies match state and action spaces!")

        return valid_policies

    def __check_policy_against_state_action_spaces(self, policy_nickname : str, policy : dict, state_space : list, action_space : list):
        # look through policy
        for conds in policy.keys():
            # get policy data point
            pol_data_point = policy[conds]
            # check data point against state and action spaces
            valid_data_point = pol_data_point.validate_data_point(state_space, action_space)
            if not valid_data_point:
                rospy.logerr("[Red Team Data Extension] Invalid %s policy data point; conditions and action not in state/action spaces; please resolve manually", policy_nickname)
                return False

        return True

    def __red_team_policy_includes_human_policy(self):
        # look through human generated policy
        for conds in self.policy_starter_reader.get_risk_mitigating_policy_data().keys():
            # get policy data point
            pol_data_point = self.policy_starter_reader.get_risk_mitigating_policy_data()[conds]
            # check if data point already exists in policy
            if pol_data_point.check_data_point_duplicated(self.policy_data):
                # data point exists in policy, check if actions conflict
                if pol_data_point.check_conflicting_data_point(self.policy_data):
                    # data point conflicts, get conflicting actions
                    _, point_act, pol_act = pol_data_point.check_and_get_conflicting_data_point(self.policy_data)
                    rospy.logerr("[Red Team Data Extension] Conflict between human-generated and red team generated policy; please resolve manually")
                    print("    Conditions:", pol_data_point.get_policy_data_point_condition_names())
                    print("    Human-generated action:", point_act)
                    print("    Red team generated action:", pol_act)
                    return False
                # otherwise, no conflict
            else:
                # add data point to policy
                self.policy_data[pol_data_point.get_policy_data_point_condition_names()] = pol_data_point

        # if we get here, human-generated policy included in red teamed policy
        rospy.loginfo("[Red Team Data Extension] Human-generated and red team generated policies agree!")
        return True
