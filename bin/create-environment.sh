#!/bin/sh

echo "Specify the environment name, or type ENTER to use gdatalog"
read name
if [ -z "$name" ]; then
    name="gdatalog"
fi

conda create --name "$name" python=3.9

conda install --yes --name "$name" pytest
conda install --yes --name "$name" -c potassco clingo
conda install --yes --name "$name -c conda-forge typeguard