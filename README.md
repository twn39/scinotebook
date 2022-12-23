## 数据分析和编程语言学习笔记

此笔记基于 jupyter notebook，安装了多个 kernel。

kernel：

 * Python
 * R

Python 安装的包：

 * Numpy
 * Scipy
 * Sympy
 * Pandas
 * Matplotlib
 * Scikit-learn

R 安装的包：

 * Ggplot2
 * Tidyverse


## Dockerfile

```
FROM continuumio/miniconda3
RUN conda install -c conda-forge jupyterlab jupyterlab-git plotly jupyter-dash dtale -y --quiet
RUN mkdir -p /opt/notebook
RUN conda install numpy scipy sympy matplotlib -y --quiet
RUN conda install -c r r-essentials -y --quiet
RUN conda install -c r r-irkernel -y --quiet


EXPOSE 8888
EXPOSE 40000
CMD ["jupyter", "lab", "--notebook-dir=/opt/notebook", "--ip=*", "--port=8888", "--no-browser", "--allow-root"]
```