import pandas as pd
import numpy as np
import os

BASE = r'c:\Users\sarat\Desktop\veri_seti\colab_training'
coached_path = f'{BASE}/data/stage4_coached_users.csv'
enriched_path = f'{BASE}/outputs/stage2_user_monthly_enriched.csv'

df_c = pd.read_csv(coached_path, encoding='utf-8-sig')
df_e = pd.read_csv(enriched_path, encoding='utf-8-sig')

actions_to_augment = ['REDUCE_EATING_OUT', 'REDUCE_SHOPPING', 'REDUCE_ENTERTAINMENT', 'INCREASE_SAVINGS']

# Find users to augment
target_users = df_c[df_c['coach_action'].isin(actions_to_augment)]['user_id'].unique()
print(f"Found {len(target_users)} users to augment.")

N_CLONES = 15 # we will create 15 clones per user

new_c_rows = []
new_e_rows = []

aug_id_counter = 1

for uid in target_users:
    user_c_data = df_c[df_c['user_id'] == uid]
    user_e_data = df_e[df_e['user_id'] == uid]
    
    for clone_idx in range(N_CLONES):
        new_uid = f'USR_AUG_{aug_id_counter:05d}'
        aug_id_counter += 1
        
        # Clone coached data
        c_clone = user_c_data.copy()
        c_clone['user_id'] = new_uid
        # Add slight noise to numeric columns
        for col in c_clone.select_dtypes(include=[np.number]).columns:
            noise = np.random.uniform(0.95, 1.05, size=len(c_clone))
            c_clone[col] = c_clone[col] * noise
        new_c_rows.append(c_clone)
        
        # Clone enriched data
        e_clone = user_e_data.copy()
        e_clone['user_id'] = new_uid
        for col in e_clone.select_dtypes(include=[np.number]).columns:
            # Add same structural noise range
            noise = np.random.uniform(0.95, 1.05, size=len(e_clone))
            e_clone[col] = e_clone[col] * noise
        new_e_rows.append(e_clone)

df_c_aug = pd.concat([df_c] + new_c_rows, ignore_index=True)
df_e_aug = pd.concat([df_e] + new_e_rows, ignore_index=True)

df_c_aug.to_csv(coached_path, index=False, encoding='utf-8-sig')
df_e_aug.to_csv(enriched_path, index=False, encoding='utf-8-sig')

print(f"Augmented data saved. Added {aug_id_counter-1} new synthetic users.")
