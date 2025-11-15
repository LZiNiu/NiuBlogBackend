## Python如何调用C++的函数（Windows）

###  1、引入pybind11 (CMake)

#### (1)下载pybind11包

方法一：可以从pybind11的GitHub页面上直接下载或者clone

```git
git clone https://github.com/pybind/pybind11.git
```

方法二：使用Python的pip以包的形式下载

```git
pip install pybind11
```

#### (2)Cmake引入pybind11

对于方法一下载的pybind包，可直接将其整体剪切到C++项目之中，下面假设项目名称为`pybind_test`，项目文件结构如下：

```
pybind_test
 |-extern
 |    |-pybind11
 |-CMakeLists.txt
```

这种直接将**pybind11**包放进项目的方式对于编写CMake文件很友好方便

> **!!注意**：windows上使用vscode和clion时配置Cmake应当指定MSVC编译器，g++无法通过编译，官网有提到“在 Windows 上，只支持 **Visual Studio 2017** 及更新版本”

对应的`CMakeLists.txt`文件如下：

```cmake
cmake_minimum_required(VERSION 3.2)

project(pybind_test)

add_subdirectory(extern/pybind11) # build子文件夹,执行pybind的CmakeLists,此处相当于引入了pybind11
pybind11_add_module(pybind_sum pybind_sum.cpp)
```

如果是方法二，通过pip下载的，并且不想将其与项目放在一起，那么需要多一些步骤

pybind11是head-only的，因此在include时只需要设置**include-path**即可

另外还需告知其Python包的位置，以Anaconda的Python虚拟环境为例，如果是base环境，需要**libs**和**include**两个文件夹来引入Python的头文件和链接库，对应路径`...\Anaconda3\libs`和`...\Anaconda3\include`，如果是其他虚拟环境，则对应路径为`...\Anaconda3\envs\{env_name}\libs`和`...\Anaconda3\envs\{env_name}\libs`，但是对于引入pybind11包来讲，我们不通过且不推荐该方式对Python进行引入，因为麻烦且易出错，出错之后对于新手不好找到解决办法。

因此选择使用CMake的`find_package`直接寻找Python路径，但需要保证设置了对应的环境变量，不只是Python，其他包例如OpenCv等，同样推荐使用`find_package`来自动寻找Python的位置。

```cmake
cmake_minimum_required(VERSION 3.2)

project(pybind_test)

# 可以加入EXACT参数指定所需的Python版本
find_package(Python3 3.8 EXACT COMPONENTS Interpreter Development REQUIRED)

#set(PYBIND11_FINDPYTHON ON)
# 通过下面的set指定pybind11的寻找路径,否则将其加入环境变量之中
set(pybind11_DIR "{your_anaconda_path}//Lib/site-packages/pybind11/share/cmake/pybind11")
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(pybind_sum pybind_sum.cpp)

```

通过以上操作，便可以将pybind11正常引入cpp项目之中，接下来使用官方例子使用pybind11。

### 2、使用pybind11

在`pybind_test`项目之下创建`pybind_sum.cpp`，此时项目结构如下：

```git
pybind_test
 |-extern
 |    |-pybind11
 |-pybind_sum.cpp
 |-CMakeLists.txt
```

在`pybind_sum.cpp`中添加如下内容：

```c++
#include <pybind11/pybind11.h>
#include <iostream>

namespace py = pybind11;

//绑定一个函数
int add(int i, int j) {
    return i + j;
}

PYBIND11_MODULE(pybind_sum, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring

    m.def("add", &add, "A function that adds two numbers");
}
```

使用Visual Studio或者Clion直接build，或者在命令行使用对应的Cmake命令。

构建完成之后，可以到对应的输出文件夹找到`pybind_sum.cp39-win_amd64.pyd`文件，在该文件位置打开终端命令行界面，运行python，依次输入以下命令即可引入并测试编写的函数，

```python
>>> import pybind_sum
>>> pybind_sum.add(1,2)
3
```

若想在其他地方使用，只需要将`.pyd`文件移动至对应位置即可。
