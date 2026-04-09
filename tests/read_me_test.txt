#at the start just run everything on the docker-compose
docker-compose up -d --build

_____________________________________

#IF YOU WANT TO RUN TEST AONE WITHOUT THE SCRIPT

#set the env
$env:WEBHOOK_SUCCESS_RATE=0; docker-compose up -d processor_servic

#run tests
docker-compose exec api_service pytest tests/

#recreate the containers again with it's default ENV rate WEBHOOK_SUCCESS_RATE
docker-compose up -d processor_service

___________________________________

#IF YOU WANT TO RUN IT ALL WITH THE SCRIPT TEST - on powershell terminal

#run this script to get permission to run it on window terminal powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

#run the tests script
./tests/run_tests.ps1