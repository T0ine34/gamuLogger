from feanor import BaseBuilder


class Builder(BaseBuilder):
    def Setup(self):
        self.addDirectory("src", "gamuLogger")
        self.addFile("readme.md")

        self.addAndReplaceByPackageVersion('pyproject.toml')
        self.addFile('LICENSE')

    def Build(self):
        self.venv().install('build')
        self.venv().runModule('build', '--outdir', f"{self.distDir}")

    def Tests(self):
        self.addDirectory('tests')
        self.venv().install('pytest')
        self.venv().runModule('pytest', f"{self.tempDir}/tests")
