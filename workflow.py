
import os.path
import os
from collections import defaultdict
from gwf import Workflow

def workflow(working_dir=os.getcwd(), 
             input_files=[], 
             output_dir=[], 
             defaults={},                                        
             Ne_list=[], 
             admix_prop_list=[],
             sel_coef_list=[],
             generations_lists=[ [] ]):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # dict of targets as info for other workflows
    targets = defaultdict(list)

    gwf = Workflow(working_dir=working_dir, defaults=defaults)

    for admix_prop in admix_prop_list:
            for sel_coef in sel_coef_list:
                for generations in generations_lists:
                    for Ne in Ne_list:
                        label = f'precomp_{Ne}_{sel_coef}_{admix_prop}_{"_".join(map(str, generations))}'
                        precomp_output_file = os.path.join(output_dir, f'{label}.txt')
                        target = gwf.target(
                            name=label,
                            inputs=input_files,
                            outputs=[precomp_output_file],
                        ) << f"""
                        mkdir -p {output_dir}
                        python precomp_traj.py --proportion {admix_prop} --selection {sel_coef} --Ne {Ne} \
                            --generations {' '.join(map(str, generations))} > $TMPDIR/{label} && mv $TMPDIR/{label} {precomp_output_file}
                        """
                        targets['trajectories'].append(target)

                        label = f'traj_{Ne}_{sel_coef}_{admix_prop}_{"_".join(map(str, generations))}'
                        traj_output_file = os.path.join(output_dir, f'{label}.txt')
                        target = gwf.target(
                            name=label,
                            inputs=[precomp_output_file],
                            outputs=[traj_output_file]
                        ) << f"""
                        mkdir -p {output_dir}
                        python tract_length.py --pdf --mode precomp --Ne {Ne} --input_file {precomp_output_file} > {traj_output_file}
                        """
                        targets['tract_length'].append(target)

    return gwf, targets

####################################################################
# Use code like this to run this as standalone workflow: 
####################################################################

# gwf, human_neanderthal_admixture_targets  = workflow(  input_files=[], 
#                                                        output_dir='steps/trajectory_data',
#                                                        defaults={'account': 'xy-drive', 'memory': '1g', 'walltime': '01:00:00'},
#                                                        Ne_list=[10000], 
#                                                        admix_prop_list=[0.10],
#                                                        sel_coef_list=[0.01],
#                                                        generations_lists=[ [2000, 3000] ])

####################################################################
# Use code like this to run this as a submodule workflow: 
####################################################################

# human_neanderthal_admixture = importlib.import_module('human-neanderthal-admixture.workflow')
# gwf, human_neanderthal_admixture_targets  = human_neanderthal_admixture.workflow(working_dir=working_dir,
#                                                        input_files=[], 
#                                                        output_dir='steps/trajectory_data',
#                                                        defaults={'account': 'xy-drive', 'memory': '1g', 'walltime': '01:00:00'},
#                                                        Ne_list=[10000], 
#                                                        admix_prop_list=[0.10],
#                                                        sel_coef_list=[0.01],
#                                                        generations_lists=[ [2000, 3000] ])
# globals()['human-neanderthal-admixture'] = gwf
