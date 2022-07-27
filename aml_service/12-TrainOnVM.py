import os, json
from azureml.core import Workspace
from azureml.core import Experiment
from azureml.core.compute import RemoteCompute
from azureml.core.runconfig import RunConfiguration
from azureml.core import ScriptRunConfig
import azureml.core
from azureml.core.authentication import AzureCliAuthentication

cli_auth = AzureCliAuthentication()
# Get workspace
ws = Workspace.from_config(auth=cli_auth)


# Read the New VM Config
with open("aml_config/security_config.json") as f:
    config = json.load(f)
remote_vm_name = config["remote_vm_name"]


# Attach Experiment
experiment_name = "devops-ai-demo"
exp = Experiment(workspace=ws, name=experiment_name)
print(exp.name, exp.workspace.name, sep="\n")

run_config = RunConfiguration()
run_config.target = remote_vm_name

# replace with your path to the python interpreter in the remote VM found earlier
run_config.environment.python.interpreter_path = "/anaconda/envs/myenv/bin/python"
run_config.environment.python.user_managed_dependencies = True


src = ScriptRunConfig(
    source_directory="./code", script="training/train.py", run_config=run_config
)
run = exp.submit(src)

# Shows output of the run on stdout.
run.wait_for_completion(show_output=True, wait_post_processing=True)

# Raise exception if run fails
if run.get_status() == "Failed":
    raise Exception(
        "Training on local env failed with following run status: {} and logs: \n {}".format(
            run.get_status(), run.get_details_with_logs()
        )
    )

# Writing the run id to /aml_config/run_id.json
run_id = {}
run_id["run_id"] = run.id
run_id["experiment_name"] = run.experiment.name
with open("aml_config/run_id.json", "w") as outfile:
    json.dump(run_id, outfile)
