#!/usr/bin/env python3
"""Phone Agent 安装配置脚本"""

from setuptools import find_packages, setup

# 读取 README.md 文件作为详细描述
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# 配置包的安装信息
setup(
    name="phone-agent",  # 包名
    version="0.1.0",  # 版本号
    author="Zhipu AI",  # 作者
    author_email="",  # 作者邮箱
    description="AI-powered phone automation framework",  # 简短描述：AI驱动的手机自动化框架
    long_description=long_description,  # 详细描述（从README读取）
    long_description_content_type="text/markdown",  # 详细描述的格式为Markdown
    url="https://github.com/yourusername/phone-agent",  # 项目主页URL
    packages=find_packages(),  # 自动查找所有包
    classifiers=[  # PyPI分类器，用于描述项目特征
        "Development Status :: 3 - Alpha",  # 开发状态：Alpha版本
        "Intended Audience :: Developers",  # 目标受众：开发者
        "License :: OSI Approved :: Apache Software License",  # 许可证：Apache 2.0
        "Operating System :: OS Independent",  # 操作系统：跨平台
        "Programming Language :: Python :: 3",  # 编程语言：Python 3
        "Programming Language :: Python :: 3.10",  # 支持Python 3.10
        "Programming Language :: Python :: 3.11",  # 支持Python 3.11
        "Programming Language :: Python :: 3.12",  # 支持Python 3.12
        "Topic :: Software Development :: Libraries :: Python Modules",  # 主题：Python模块库
        "Topic :: Scientific/Engineering :: Artificial Intelligence",  # 主题：人工智能
    ],
    python_requires=">=3.10",  # Python版本要求：至少3.10
    install_requires=[  # 核心依赖包
        "Pillow>=12.0.0",  # 图像处理库
        "openai>=2.9.0",  # OpenAI API客户端
    ],
    extras_require={  # 可选依赖包
        "dev": [  # 开发环境依赖
            "pytest>=7.0.0",  # 测试框架
            "black>=23.0.0",  # 代码格式化工具
            "mypy>=1.0.0",  # 静态类型检查工具
            "ruff>=0.1.0",  # 代码检查工具
        ],
    },
    entry_points={  # 命令行入口点
        "console_scripts": [
            "phone-agent=main:main",  # 创建phone-agent命令，指向main模块的main函数
        ],
    },
)
