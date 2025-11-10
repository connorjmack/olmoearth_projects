# Mozambique LULC and Crop Type Classification

This project has two main tasks:
	1.	Land Use/Land Cover (LULC) and cropland classification
	2.	Crop type classification

The annotations come from field surveys across three provinces in Mozambique: Gaza, Zambezia, and Manica.

For LULC classification, the train/test splits are:
- Gaza: 2,262 / 970
- Manica: 1,917 / 822
- Zambezia: 1,225 / 525

### Finetuning

Currently, we use [rslearn_projects](github.com/allenai/rslearn_projects) for finetuning, using the [rslp_finetuning.yaml](rslp_finetuning.yaml). To run finetune for a specific province, update the yaml's `groups` (lines 238-250) from `"gaza"` to one of `["gaza", "manica", "zambezia"]`. With `rslean_projects` installed (and access to Beaker), finetuning can then be run with the following command:

```
python -m rslp.main olmoearth_pretrain launch_finetune --image_name gabrielt/rslpomp_20251027b --config_paths+=data/helios/v2_mozambique_lulc/finetune_s2_20251024.yml --cluster+=ai2/saturn --rslp_project <MY_RSLP_PROJECT_NAME> --experiment_id <MY_EXPERIMENT_ID>
```
