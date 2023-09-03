import os


def prepare_output_folder():
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir, 'output/')

    if not os.path.isdir(results_dir):
        os.makedirs(results_dir)
