source ~/miniconda3/etc/profile.d/conda.sh
cd ~/budgeteer
conda activate budget

export http_proxy=http://172.16.2.30:8080/
export https_proxy=https://172.16.2.30:8080/

git checkout master
python main.py
