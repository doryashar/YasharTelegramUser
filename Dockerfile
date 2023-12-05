FROM python:3.9 

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
# RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY ./src /app/src
COPY ./db /app/db
COPY .env *.session ./

# RUN pip install requests beautifulsoup4 python-dotenv
ENTRYPOINT [ "python" ]
CMD [ "./src/main.py" ,"telegram_gatherer", "processor", "telegram_broadcaster"]
# CMD [“python3”, “./main.py”] 
# CMD [ "find" ]
