import argparse
import os
import sys

import pandas as pd
from sklearn.preprocessing import StandardScaler

sys.path.append('..')
from modeling.utils import setup_logger
from dataset_generating_scripts.data_processing_utils import window_truncate, add_artificial_mask, saving_into_h5

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate geomagnetic dataset')
    parser.add_argument("--file_path", help='path of dataset file', type=str)
    parser.add_argument("--artificial_missing_rate", help='artificially mask out additional values',
                        type=float, default=0.1)
    parser.add_argument("--seq_len", help='sequence length', type=int, default=100)
    parser.add_argument('--dataset_name', help='name of generated dataset, will be the name of saving dir', type=str,
                        default='test')
    parser.add_argument('--saving_path', type=str, help='parent dir of generated dataset', default='.')
    args_2 = parser.parse_args()

    dataset_saving_dir = os.path.join(args_2.saving_path, args_2.dataset_name)
    if not os.path.exists(dataset_saving_dir):
        os.makedirs(dataset_saving_dir)

    logger = setup_logger(os.path.join(dataset_saving_dir + "/dataset_generating.log"),
                          'Generate Geomagnetic dataset', mode='w')
    logger.info(args_2)

    df_collector = []
    station_name_collector = []
    file_list = os.listdir(args_2.file_path)
    for filename in file_list:
        file_path = os.path.join(args_2.file_path, filename)
        current_df = pd.read_csv(file_path)
        current_df['date_time'] = pd.to_datetime(current_df[['year', 'month', 'day']])
        station_name_collector.append(current_df.loc[0, 'station'])
        current_df = current_df.drop(['No','year','month','day','min','station'], axis=1)
        df_collector.append(current_df)
        logger.info(f'reading {file_path}, data shape {current_df.shape}')

    logger.info(f'There are total {len(station_name_collector)} stations, they are {station_name_collector}')
    date_time = df_collector[0]['date_time']
    df_collector = [i.drop('date_time', axis=1) for i in df_collector]
    df = pd.concat(df_collector, axis=1)
    args_2.feature_names = [station + '_' + feature
                          for station in station_name_collector
                          for feature in df_collector[0].columns]
    args_2.feature_num = len(args_2.feature_names)
    df.columns = args_2.feature_names
    logger.info(f'Original df missing rate: '
                f'{(df[args_2.feature_names].isna().sum().sum() / (df.shape[0] * args_2.feature_num)):.3f}')

    df['date_time'] = date_time
    unique_months = df['date_time'].dt.to_period('M').unique()

    # divide train/validation/test set
    selected_as_train = unique_months[2:]
    logger.info(f'months selected as train set are {selected_as_train}')
    selected_as_val = unique_months[:1]
    logger.info(f'months selected as val set are {selected_as_val}')
    selected_as_test = unique_months[1:2]
    logger.info(f'months selected as test set are {selected_as_test}')
    train_set = df[df['date_time'].dt.to_period('M').isin(selected_as_train)]
    val_set = df[df['date_time'].dt.to_period('M').isin(selected_as_val)]
    test_set = df[df['date_time'].dt.to_period('M').isin(selected_as_test)]



    scaler = StandardScaler()
    train_set_X = scaler.fit_transform(train_set.loc[:, args_2.feature_names])
    val_set_X = scaler.transform(val_set.loc[:, args_2.feature_names])
    test_set_X = scaler.transform(test_set.loc[:, args_2.feature_names])

    # print('train_set_X:'+str(train_set_X))
    print('test_set_X_shape:' + str(test_set_X.shape))

    # train_set_X = (train_set.loc[:, args_2.feature_names])
    # val_set_X = (val_set.loc[:, args_2.feature_names])
    # test_set_X = (test_set.loc[:, args_2.feature_names])

    train_set_X = window_truncate(train_set_X, args_2.seq_len)
    val_set_X = window_truncate(val_set_X, args_2.seq_len)
    test_set_X = window_truncate(test_set_X, args_2.seq_len)

    train_set_dict = add_artificial_mask(train_set_X, args_2.artificial_missing_rate, 'train')
    val_set_dict = add_artificial_mask(val_set_X, args_2.artificial_missing_rate, 'val')
    test_set_dict = add_artificial_mask(test_set_X, args_2.artificial_missing_rate, 'test')
    logger.info(f'In val set, num of artificially-masked values: {val_set_dict["indicating_mask"].sum()}')
    logger.info(f'In test set, num of artificially-masked values: {test_set_dict["indicating_mask"].sum()}')

    processed_data = {
        'train': train_set_dict,
        'val': val_set_dict,
        'test': test_set_dict
    }

    logger.info(f'Feature num: {args_2.feature_num},\n'
                f'Sample num in train set: {len(train_set_dict["X"])}\n'
                f'Sample num in val set: {len(val_set_dict["X"])}\n'
                f'Sample num in test set: {len(test_set_dict["X"])}\n')

    saving_into_h5(dataset_saving_dir, processed_data, classification_dataset=False)
    logger.info(f'All done. Saved to {dataset_saving_dir}.')
