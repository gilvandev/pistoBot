import sys
import yaml
import logging
import argparse
import gpt_2_simple as gpt2  # Memo: tf 1.x needed
from os import makedirs
from os.path import basename, normpath, join
from datetime import datetime

sys.path.append("./")  # needed 4 utils imports - created according to launcher
from pistoBot.utils.general_utils import my_init, load_yaml


def run(path_params: str, local: bool):
    # Input
    params = load_yaml(path_params)
    params_data = params['data']
    params_ml = params['ml']
    params_gen = params['generation']
    logging.debug(f"Params: {params}")

    # Init
    gpt2.download_gpt2(model_name="124M")
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    model_dir = join(params_ml['save_path'], f"02_gp2_simple_{timestamp}")

    # Fine-tune
    sess = gpt2.start_tf_sess()

    gpt2.finetune(sess,
                  dataset=params_data['file_path'],
                  model_dir=model_dir,
                  model_name=params_ml['model_size'],
                  steps=params_ml['steps'],
                  restore_from=params_ml['restore_from'],
                  run_name=params_ml['run_name'],
                  print_every=params_ml['print_every'],
                  sample_every=params_ml['sample_every'],
                  save_every=params_ml['save_every'])

    # Generate
    text_generated = gpt2.generate(sess,
                                   run_name=params_ml['run_name'],
                                   model_dir=model_dir,
                                   prefix=params_gen['prefix'],
                                   temperature=params_gen['temperature'],
                                   return_as_list=True)

    # Output persist
    model_params_path = join(model_dir, 'gpt2_simple_params.yaml')
    with open(model_params_path, 'w') as f:
        yaml.dump(params, f, default_flow_style=False)
    logging.debug(f"Model params saved at {model_params_path}")

    makedirs(join(model_dir, 'text_generated'), exist_ok=True)
    text_generated_path = join(model_dir, 'text_generated', f'{timestamp}.txt')
    open(text_generated_path, 'w').writelines('\n'.join(text_generated))

    logging.debug(f"Text generated saved at {text_generated_path} - {len(text_generated)} total lines")


def main(argv):
    parser = argparse.ArgumentParser(prog=argv[0])
    parser.add_argument("--path_params", help="Path to rnn YAML params",
                        default="./pistoBot/02_gpt2_simple/gpt2_simple_params.yaml")
    parser.add_argument("--local", help="set if code is not running on colab", action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args(argv[1:])
    loglevel = logging.DEBUG if args.verbose else logging.INFO
    process_name = basename(normpath(argv[0]))
    logging.basicConfig(format=f"[{process_name}][%(levelname)s]: %(message)s", level=loglevel, stream=sys.stdout)
    run_initialized = my_init(run, args.local)
    delattr(args, "verbose")
    run_initialized(**vars(args))


if __name__ == '__main__':
    main(sys.argv)
