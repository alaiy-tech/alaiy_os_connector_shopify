from setuptools import setup, find_packages

with open("requirements.txt") as f:
    # Comments and blank lines are stripped rather than passed through: the file
    # explains why each of the image dependencies is here, and a "#" line handed
    # to install_requires is not a requirement specifier — it fails the build.
    install_requires = [
        line.strip()
        for line in f
        if line.strip() and not line.lstrip().startswith("#")
    ]

setup(
    name="alaiy_os_connector_shopify",
    version="0.0.1",
    description="Shopify sales channel connector for AlaiyOS",
    author="Alaiy OS",
    author_email="dev@alaiy.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
