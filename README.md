# Generateing Categories
Code and participant data for ["Creating Something Different: Similarity, Contrast, and Representativeness in Categorization"](https://doi.org/10.1007/s42113-024-00209-5) published in Computational Brain & Behavior in 2024.

## Authors
Code written by Nolan Conway, Shi Xian Liew, and Joseph Austerweil.
The branch `kesong` has code written by Kesong Cao.

## License
MIT License -- any use of these files is at your own risk. By using this code, you accept these terms.

## Configuration
You can install the python environment via conda using: `conda create --name myenv --file spec_file.txt`

    Note: This likely only works for linux64 builds (possibly WSL2 only, which is what created it).

For Mac (Apple Silicon) users, use `conda create --name myenv --file spec-file-mac-arm.txt` or `conda env create -f environment-mac-arm.yml`.

Remember pickle_compat needs to installed via pip (`pip install pickle-compat`) or conda-forge (`conda install conda-forge::pickle-compat`).

## Usage
The overall model code is in the `Modules` directory and can be called from there. You are best off learning how to do that by rerunning our analyses and the code that generates the different figures in the paper.

The `Experiments/` folder contains these scripts. They are contained within `xor_cluster_row/` (Experiment 1), `middle_bottom/` (Experiment 2), `corner/` (Experiment 3), `multiexpt_modeling` (Modeling that covers more than one experiment), and `jernkemp2023_e3` (Our re-analysis of Experiment 3 from Jern & Kemp, 2013 that is contained in the supplementary material).

## Contact
The corresponding author is Joseph Austerweil. Please reach out to him at `joseph.austerweil@gmail.com` with any questions/comments.

Thanks and enjoy! \
Joe