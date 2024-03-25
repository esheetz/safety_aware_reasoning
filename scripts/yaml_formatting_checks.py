"""
YAML State Action Space Checks Class
Emily Sheetz, NSTGRO VTE 2024
"""

import os

from likelihood_consequence_risk import LikelihoodLevels, ConsequenceClasses

###################################
### YAML FILE FORMATTING CHECKS ###
###################################

class YAMLChecks:

    # CHECK YAML FILE EXISTENCE

    @staticmethod
    def check_yaml_existence(yaml_file_path):
        # check if given YAML file exists and is a file
        return (os.path.exists(yaml_file_path) and
                os.path.isfile(yaml_file_path))

    # CHECK YAML FORMATTING

    @staticmethod
    def check_yaml_formatting(file_nickname, yaml_dict, env_name, list_key, list_elem_keys):
        # check if environment exists
        if env_name not in yaml_dict.keys():
            print("ERROR: environment " + env_name + " does not exist in " + file_nickname + " file")
            return False

        # check for list key
        if list_key not in yaml_dict[env_name].keys():
            print("ERROR: environment " + env_name + " has no " + file_nickname + "s defined under key '" + list_key + "'")
            return False

        # get number of elements in list
        num_elems = len(yaml_dict[env_name][list_key])

        # initialize valid elements flag
        valid_elems = True

        # check each element in list
        for i in range(num_elems):
            # get element
            elem = yaml_dict[env_name][list_key][i]

            # check for each key in list element
            for elem_key in list_elem_keys:
                if elem_key not in elem.keys():
                    print("ERROR: " + file_nickname + " " + str(i) + " of " + str(num_elems) + " does not have a " + elem_key)
                    valid_elems = False

        return valid_elems



#####################################
### STATE SPACE FORMATTING CHECKS ###
#####################################

class YAMLStateSpaceChecks(YAMLChecks):

    @staticmethod
    def check_risky_condition_yaml_formatting(yaml_dict, env_name):
        return YAMLChecks.check_yaml_formatting(file_nickname="risky condition",
                                                yaml_dict=yaml_dict,
                                                env_name=env_name,
                                                list_key="conditions",
                                                list_elem_keys=["name","likelihood","consequence"])

    @staticmethod
    def check_valid_risky_condition_values(cond_dict, i, num_conds):
        # initialize valid values flag
        valid_values = True

        # check for valid name
        if not type(cond_dict['name']) == str:
            print("WARN: non-string name for risky condition " + str(i) + " of " + str(num_conds))
            valid_values = False

        # check for valid likelihood and consequence scores
        if not LikelihoodLevels.valid_value(cond_dict['likelihood']):
            print("WARN: invalid likelihood value for risky condition " + str(i) + " of " + str(num_conds))
            valid_values = False

        if not ConsequenceClasses.valid_value(cond_dict['consequence']):
            print("WARN: invalid consequence value for risky condition " + str(i) + " of " + str(num_conds))
            valid_values = False

        return valid_values



######################################
### ACTION SPACE FORMATTING CHECKS ###
######################################

class YAMLActionSpaceChecks(YAMLChecks):

    @staticmethod
    def check_risk_mitigating_action_yaml_formatting(yaml_dict, env_name):
        return YAMLChecks.check_yaml_formatting(file_nickname="risk mitigating action",
                                                yaml_dict=yaml_dict,
                                                env_name=env_name,
                                                list_key="actions",
                                                list_elem_keys=["name"])

    @staticmethod
    def check_valid_risk_mitigating_action_values(act_dict, i, num_acts):
        # initialize valid values flag
        valid_values = True

        # check for valid name
        if not type(act_dict['name']) == str:
            print("WARN: non-string name for risk mitigating action " + str(i) + " of " + str(num_acts))
            valid_values = False

        return valid_values



########################################
### POLICY STARTER FORMATTING CHECKS ###
########################################

class YAMLPolicyStarterChecks(YAMLChecks):

    @staticmethod
    def check_risk_mitigating_policy_starter_yaml_formatting(yaml_dict, env_name):
        return YAMLChecks.check_yaml_formatting(file_nickname="risk mitigating policy starter",
                                                yaml_dict=yaml_dict,
                                                env_name=env_name,
                                                list_key="policy_starter",
                                                list_elem_keys=["conditions", "action"])

    @staticmethod
    def check_valid_risk_mitigating_policy_starter_values(pol_dict, i, num_pols):
        # TODO
        return False
