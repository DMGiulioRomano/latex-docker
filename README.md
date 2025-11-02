# LaTeX in Docker (Ubuntu Edition)

[![GitHub license](https://img.shields.io/github/license/DMGiulioRomano/latex-docker-ubuntu)](https://github.com/DMGiulioRomano/latex-docker-ubuntu/blob/main/LICENSE)
[![GitHub build status](https://img.shields.io/github/actions/workflow/status/DMGiulioRomano/latex-docker-ubuntu/docker.yaml?branch=main)](https://github.com/DMGiulioRomano/latex-docker-ubuntu/actions)
[![GitHub release](https://img.shields.io/github/v/release/DMGiulioRomano/latex-docker-ubuntu)](https://github.com/DMGiulioRomano/latex-docker-ubuntu/releases)

[![GitHub Container Registry](https://img.shields.io/badge/ghcr.io-dmgiulioromano%2Flatex--docker--ubuntu-blue?logo=github&logoColor=white)](https://github.com/DMGiulioRomano/latex-docker-ubuntu/pkgs/container/latex-docker-ubuntu)
[![DockerHub](https://img.shields.io/badge/docker.io-dmgiulioromano%2Flatex--docker--ubuntu-blue)](https://hub.docker.com/r/dmgiulioromano/latex-docker-ubuntu)

[![Docker Image Size (minimal)](https://img.shields.io/docker/image-size/dmgiulioromano/latex-docker-ubuntu/minimal?label=minimal)](https://hub.docker.com/r/dmgiulioromano/latex-docker-ubuntu)
[![Docker Image Size (basic)](https://img.shields.io/docker/image-size/dmgiulioromano/latex-docker-ubuntu/basic?label=basic)](https://hub.docker.com/r/dmgiulioromano/latex-docker-ubuntu)
[![Docker Image Size (small)](https://img.shields.io/docker/image-size/dmgiulioromano/latex-docker-ubuntu/small?label=small)](https://hub.docker.com/r/dmgiulioromano/latex-docker-ubuntu)
[![Docker Image Size (medium)](https://img.shields.io/docker/image-size/dmgiulioromano/latex-docker-ubuntu/medium?label=medium)](https://hub.docker.com/r/dmgiulioromano/latex-docker-ubuntu)
[![Docker Image Size (full)](https://img.shields.io/docker/image-size/dmgiulioromano/latex-docker-ubuntu/full?label=full)](https://hub.docker.com/r/dmgiulioromano/latex-docker-ubuntu)

This repository defines a set of Docker images for running LaTeX in containers, optimized for CI/CD workflows and local development. Built on **Ubuntu 22.04 LTS**, these images provide a stable and reliable foundation for LaTeX compilation.

The images come in several variants corresponding to TeX Live schemes, from minimal installations to complete distributions. The default scheme is `full`, which contains all packages for maximum compatibility.

If a package is missing, you can always use `tlmgr` to install it. Since the images are based on **Ubuntu**, system packages can be installed using `apt-get`.

| Scheme  | Image                                              | Size     |
|---------|---------------------------------------------------|----------|
| minimal | `dmgiulioromano/latex-docker-ubuntu:latest-minimal` | ~150 MB  |
| basic   | `dmgiulioromano/latex-docker-ubuntu:latest-basic`   | ~250 MB  |
| small   | `dmgiulioromano/latex-docker-ubuntu:latest-small`   | ~400 MB  |
| medium  | `dmgiulioromano/latex-docker-ubuntu:latest-medium`  | ~800 MB  |
| full    | `dmgiulioromano/latex-docker-ubuntu:latest`         | ~3 GB    |

The images use a layered architecture where each variant builds upon the previous one. For example, `full` adds packages to `medium`, which extends `small`, and so on. This approach optimizes storage space and build efficiency.

## Quick Start

For a simple LaTeX compilation, assuming you have a file named `main.tex` in your current directory:

```shell
docker run --rm -v "$PWD:/src" -w /src -u "$UID:$GID" \
  dmgiulioromano/latex-docker-ubuntu:latest \
  latexmk -pdf -outdir=out -auxdir=out/aux main.tex
```

This command will:
- Mount your current directory to `/src` in the container
- Set the working directory to `/src`
- Run as your user to maintain file permissions
- Compile `main.tex` to PDF in the `out` directory

## Usage Examples

### Live Compilation (Watch Mode)

For continuous compilation during development:

```shell
docker run --rm -v "$PWD:/src" -w /src -u "$UID:$GID" \
  dmgiulioromano/latex-docker-ubuntu:latest \
  latexmk -pdf -pvc -outdir=out -auxdir=out/aux main.tex
```

The `-pvc` flag enables "preview continuously" mode, automatically recompiling when source files change.

### Alternative LaTeX Engines

For XeLaTeX compilation:
```shell
docker run --rm -v "$PWD:/src" -w /src -u "$UID:$GID" \
  dmgiulioromano/latex-docker-ubuntu:latest \
  latexmk -xelatex -outdir=out main.tex
```

For LuaLaTeX compilation:
```shell
docker run --rm -v "$PWD:/src" -w /src -u "$UID:$GID" \
  dmgiulioromano/latex-docker-ubuntu:latest \
  latexmk -lualatex -outdir=out main.tex
```

### Direct LaTeX Commands

If you prefer not to use `latexmk`, you can run any LaTeX command directly:

```shell
docker run --rm -v "$PWD:/src" -w /src -u "$UID:$GID" \
  dmgiulioromano/latex-docker-ubuntu:latest \
  pdflatex main.tex
```

### Installing Additional Tools

For complex build processes, you might need additional tools like `make`:

```shell
docker run --rm -v "$PWD:/src" -w /src -u "$UID:$GID" \
  dmgiulioromano/latex-docker-ubuntu:latest \
  sh -c "apt-get update && apt-get install -y make && make"
```

## Useful latexmk Options

- `-c` - Clean auxiliary files
- `-g` - Force compilation even if no changes detected
- `-silent` - Suppress output except for errors
- `-f` - Force compilation even after errors
- `-interaction=nonstopmode` - Don't pause for errors

See the [latexmk documentation](https://ctan.gust.org.pl/tex-archive/support/latexmk/latexmk.pdf) for complete usage and options.

## Versioning Strategy

### Stable Versions

Stable versions follow the format `<major>.<minor>` (e.g., `2025.1`), where:
- **Major version**: Corresponds to the TeX Live year
- **Minor version**: Image version within that TeX Live release

Stable versions provide:
- Tested and verified package sets
- Security updates and bug fixes
- Consistent package versions for reproducible builds

| TeX Live Version | Latest Stable |
|-----------------|---------------|
| 2025            | `2025.1`      |
| 2024            | `2024.1`      |

### Development Versions

Development versions are built automatically and include:

1. **`devel`** - Latest development build (⚠️ **not recommended for production**)
2. **`devel-<TL_VERSION>-<DATE>`** - Historic builds with working `tlmgr`
3. **`devel-<TL_VERSION>`** - Latest build for specific TeX Live version
4. **`devel-any-<DATE>`** - Build from specific date without TeX Live version

## CI/CD Integration

### GitHub Actions

```yaml
name: Compile LaTeX Document
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    container: dmgiulioromano/latex-docker-ubuntu:latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Compile LaTeX document
        run: latexmk -pdf -output-directory=dist main.tex

      - name: Upload PDF artifact
        uses: actions/upload-artifact@v4
        with:
          name: compiled-document
          path: dist/main.pdf
```

### GitLab CI/CD

```yaml
stages:
  - build

compile_latex:
  stage: build
  image: dmgiulioromano/latex-docker-ubuntu:latest
  script:
    - latexmk -pdf -output-directory=dist main.tex
  artifacts:
    paths:
      - dist/main.pdf
    expire_in: 1 week
```

### Docker Compose

For local development with hot reload:

```yaml
version: '3.8'
services:
  latex:
    image: dmgiulioromano/latex-docker-ubuntu:latest
    volumes:
      - .:/workspace
    working_dir: /workspace
    command: latexmk -pdf -pvc -outdir=out main.tex
    user: "${UID}:${GID}"
```

## Image Variants Comparison

| Variant | Best For | Includes |
|---------|----------|----------|
| **minimal** | Basic documents, CI/CD optimization | Core LaTeX, basic packages |
| **basic** | Simple articles, letters | Common document classes, basic fonts |
| **small** | Academic papers, reports | Math packages, bibliography tools |
| **medium** | Complex documents, presentations | Beamer, advanced graphics, more fonts |
| **full** | Publishing, complete workflows | All TeX Live packages |

## Package Management

### Installing Missing Packages

```shell
# Run container interactively
docker run -it --rm -v "$PWD:/src" -w /src \
  dmgiulioromano/latex-docker-ubuntu:latest bash

# Inside container, install packages
tlmgr install <package-name>
```

### Updating Packages

```shell
# Update package database
tlmgr update --self

# Update all packages
tlmgr update --all
```

## Advanced Usage

### Multi-stage Docker Builds

For optimized production images:

```dockerfile
FROM dmgiulioromano/latex-docker-ubuntu:medium as builder
COPY . /workspace
WORKDIR /workspace
RUN latexmk -pdf main.tex

FROM alpine:latest
COPY --from=builder /workspace/main.pdf /output/
```

### Custom Font Installation

```shell
# Install system fonts
apt-get update && apt-get install -y fonts-liberation

# Or copy custom fonts
COPY fonts/ /usr/share/fonts/custom/
fc-cache -fv
```

## Troubleshooting

### Permission Issues

Ensure you run with proper user permissions:
```shell
docker run --rm -v "$PWD:/src" -w /src -u "$(id -u):$(id -g)" \
  dmgiulioromano/latex-docker-ubuntu:latest latexmk -pdf main.tex
```

### Missing Packages

If compilation fails due to missing packages:
```shell
# Use a larger image variant
docker run --rm -v "$PWD:/src" -w /src \
  dmgiulioromano/latex-docker-ubuntu:full latexmk -pdf main.tex

# Or install the specific package
docker run --rm -v "$PWD:/src" -w /src \
  dmgiulioromano/latex-docker-ubuntu:latest \
  sh -c "tlmgr install <package-name> && latexmk -pdf main.tex"
```

### Font Issues

For documents requiring specific fonts:
```shell
# Install additional font packages
docker run --rm -v "$PWD:/src" -w /src \
  dmgiulioromano/latex-docker-ubuntu:latest \
  sh -c "apt-get update && apt-get install -y fonts-<font-package> && latexmk -pdf main.tex"
```

## Contributing

Contributions are welcome! Please see our [contributing guidelines](CONTRIBUTING.md) for details on:
- Reporting issues
- Submitting pull requests
- Development setup
- Testing procedures

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project is based on the excellent work by [kjarosh/latex-docker](https://github.com/kjarosh/latex-docker), adapted for Ubuntu-based environments to provide better compatibility with certain LaTeX packages and system dependencies.

## Support

- 📖 [Documentation](https://github.com/DMGiulioRomano/latex-docker-ubuntu/wiki)
- 🐛 [Issue Tracker](https://github.com/DMGiulioRomano/latex-docker-ubuntu/issues)
- 💬 [Discussions](https://github.com/DMGiulioRomano/latex-docker-ubuntu/discussions)
- 🐳 [Docker Hub](https://hub.docker.com/r/dmgiulioromano/latex-docker-ubuntu)
