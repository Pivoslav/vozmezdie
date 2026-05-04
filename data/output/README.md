# `data/output` (experiment redo)

This directory is intentionally **empty** until you run the pipeline again.

Previous pipeline artifacts were moved to:

`data/archive/pre_experiment_redo_<timestamp>/output`

Restore instructions are in `README_RESTORE.txt` inside that archive folder.

After assessments are ready, regenerate outputs with:

```bash
export PIPELINE_CONFIG=config/pipeline_config.experiment_redo.json
python run.py --agent-assessments --agent-assessments-file=data/experiments/exp_a_human_slices/agent_assessments.json
```

(Run again with Experiment B’s file when evaluating that experiment.)
