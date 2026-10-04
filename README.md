# Mines

忠实本地化 [Simon Tatham 的 Mines 网页版](https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/mines.html)，只保留原版操作菜单、棋盘和状态栏，不显示原网页的标题介绍、下方说明、分享文字及站点页脚。

## GitHub Pages 部署

仓库根目录的 `index.html` 已是完整可运行版本，无需安装依赖或在线构建。

在仓库 **Settings → Pages** 中选择：

| 设置 | 值 |
| --- | --- |
| Source | Deploy from a branch |
| Branch | main |
| Folder | / (root) |

保存并等待 GitHub 部署完成。默认访问地址为 `https://yunyuyuan.github.io/mines/`。仓库已经包含 `.nojekyll`，不需要 Jekyll。所有脚本和 WebAssembly 都内嵌在 HTML 中，不依赖站点根路径、CDN 或远程 API，因此项目子路径 `/mines/` 可直接使用。

本次仅提交部署文件，不自动开启或更改 GitHub Pages 设置。

## 本地运行

直接下载并使用现代浏览器打开 `index.html`，即可完全离线游玩，无需服务器、安装或账号。

桌面操作与原版相同：左键开格，右键插旗或取消旗帜；满足旗帜数量的数字格可点击展开周围。保留原版键盘和组合点击。触摸设备点按开格，长按 450 毫秒插旗。右下角手柄可拖动棋盘尺寸，右键手柄恢复默认尺寸。

保留原版 Game、Type、新局、重开、撤销、重做、求解、偏好设置、游戏 ID、随机种子、存档导入导出、自定义参数与所有棋盘类型。默认 9×9 / 10 雷。

## 复刻方式

直接使用官方发布的 JavaScript 与 WebAssembly 引擎（`20260923.616da16`），不是重新编写近似扫雷。原版棋盘绘制、首步安全、默认无猜测生成、游戏规则及鼠标键盘输入未修改。

打包时仅增加内嵌 WebAssembly 的加载桥接，以支持 `file://` 双击离线打开；另外增加移动端宽度约束、viewport 和长按输入桥接。引擎原始文件和输出文件 SHA-256 记录在 `SOURCE.json`。

## 源码与构建

| 路径 | 用途 |
| --- | --- |
| index.html | GitHub Pages 首页与离线单文件游戏 |
| public/index.html | 同一构建产物，供本地测试使用 |
| src/ | 精简页面结构、原版 CSS 与触摸桥接 |
| vendor/ | 未修改的上游 HTML、JS、WASM 与 MIT 许可 |
| scripts/build.py | 生成根目录和 public 目录的独立 HTML |
| tests/verify.py | 离线启动、原版画布对照、交互及移动触摸回归 |

修改 `src/` 后，运行：

```sh
python3 scripts/build.py
```

提交更新后的 `index.html` 即可部署，不需要 npm 或其他构建依赖。

可选本地 HTTP 预览：

```sh
python3 -m http.server 3000
```

访问 `http://localhost:3000/`。此服务器仅用于预览，游戏本身不依赖服务器。

## 验证

已通过 11 项 Chromium 集成检查，页面异常为 0。相同种子下的默认棋盘、首次开格、插旗和重开画布与未经修改的原版逐像素一致；撤销、重做、求解、踩雷与失败撤销、设置、游戏 ID、存档导出、移动点按和长按均通过检查。原版其他浏览器支持路径保留，但未逐一实测。

回归测试需自行安装 Python Playwright，并使 Chromium 位于 `/usr/bin/chromium`，随后运行 `python3 tests/verify.py`。这些仅为测试依赖，部署和游玩不需要。

## 许可与来源

保留仓库原有的 Apache-2.0 `LICENSE`。第三方 Simon Tatham 游戏代码按其原始 MIT 许可使用，完整声明在 [`vendor/LICENSE`](vendor/LICENSE)；输出 HTML 中也内嵌该声明，未重新许可第三方代码。

参考：[原版游戏](https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/mines.html)、[官方游戏文档](https://www.chiark.greenend.org.uk/~sgtatham/puzzles/doc/mines.html)、[官方许可](https://www.chiark.greenend.org.uk/~sgtatham/puzzles/doc/licence.html)。
