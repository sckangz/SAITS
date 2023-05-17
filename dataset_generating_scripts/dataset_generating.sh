# generate magnetic dataset
python gene_jupiter_mag_dataset.py \
  --file_path RawData/Geomagnetic/jupiter\
  --seq_len 1000 \
  --artificial_missing_rate 0.1 \
  --dataset_name Jupiter_seqlen1000_01masked\
  --saving_path ../generated_datasets