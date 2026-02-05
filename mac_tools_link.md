# new mac

## brew(必须的必)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```


## wget curl git

```bash
brew install wget curl git
```

## 终端

### iterm2

```bash
brew install --cask iterm2
```

### oh my zsh

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

### 可选插件 zsh
brew install zsh-syntax-highlighting zsh-autosuggestions
```

## 编辑器 ide

### vscode

```bash
brew install --cask visual-studio-code

brew install --cask jetbrains-toolbox
然后在 toolbox中安装，激活搜索 nav.020417.xyz 中搜激活
```

## 开发环境

### node

```bash
nvm环境管理
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
安装 lts 版本  nvm install --lts
```

### python

```bash
brew install python3
# 虚拟环境
python3 -m pip install --user virtualenv
# uv 管理环境
brew install uv
```

### ruby

```bash
brew install ruby
```

### java/jdk

```bash
brew install openjdk@17
sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk
```

### go

```bash
brew install go
```

### docker

```bash
brew install --cask docker
# 也可以安装软件 orbstack
``` 

### 数据库工具

```bash
# gui 数据库客户端
brew install --cask tableplus
brew install --cask dbeaver-community
```

## api/网络

### postman/paw

```bash
brew install --cask postman
brew install --cask paw
```

### Insomnia

```bash
brew install --cask insomnia
```

## 效率工具

### Raycast

```bash
# 替代 Spotlight，启动器 + 剪贴板 + 窗口管理
brew install --cask raycast
```

### Rectangle（窗口分屏）

```bash
brew install --cask rectangle
```

### The Unarchiver（解压）

```bash
brew install --cask the-unarchiver
```

## 浏览器

```bash
brew install --cask google-chrome
brew install --cask firefox
```

## 设计/抓包/文档

### figma

```bash
brew install --cask figma
```

### wireshark/charles

```bash
brew install --cask wireshark
brew install --cask charles paw
```

### Notion / Obsidian/kaleidoscope

```bash
brew install --cask kaleidoscope 
brew install --cask notion
brew install --cask obsidian
```

## 其他补充

```bash
# 效率工具
brew install --cask alfred cleanshot magnet raycast

# 文件与传输
brew install --cask path-finder localsend keka daisydisk

# 多媒体
brew install --cask iina losslesscut downie

# PDF与办公
brew install --cask pdf-expert liquidtext
```
