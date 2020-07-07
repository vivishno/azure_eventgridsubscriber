FROM marvinbuss/aml-docker:latest

LABEL maintainer="azure/gh-aml"

RUN python -m pip install --upgrade pip
RUN python -m pip install azure-cli
# RUN apt-get -y -qq update && \
# 	apt-get install -y -qq curl && \
# 	apt-get clean
# #
# # install jq to parse json within bash scripts
# RUN curl -o /usr/local/bin/jq http://stedolan.github.io/jq/download/linux64/jq && \
#   chmod +x /usr/local/bin/jq


COPY /code /code
ENTRYPOINT ["/code/entrypoint.sh"]
