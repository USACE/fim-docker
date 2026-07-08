 #!/bin/bash

# Define the target directory

# directories=("./UPDATE/DEV" "./UPDATE/PROD")
directories=("./UPDATE/TEST")

# Loop through files in the target directory
for directory in "${directories[@]}"; do
  # Check if the target is not a directory
  if [ ! -d "$directory" ]; then
    exit 1
  fi
  environment=$(basename "$directory")
  repo="038611608639.dkr.ecr.us-east-1.amazonaws.com"
  if [ "$environment" == "PROD" ]; then
    repo="648157167324.dkr.ecr.us-gov-west-1.amazonaws.com"
  fi
  if [ "$environment" == "TEST" ]; then
    repo="276847049069.dkr.ecr.us-gov-west-1.amazonaws.com"
  fi
  for file in "$directory"/*; do
    if [ -f "$file" ]; then
        xbase=${file##*/}
        xfilename=${xbase%.*}
      if [ "$xfilename" == "esd-download-api" ] || [ "$xfilename" == "esd-upload-api" ]; then
          echo "$file"
          echo "$xfilename"
          # echo 038611608639.dkr.ecr.us-east-1.amazonaws.com/$xfilename:release
          echo $repo/$xfilename:test
          docker build -t $xfilename -f $file --no-cache .
          docker tag $xfilename $repo/$xfilename:test
          docker push $repo/$xfilename:test
      # else
      #     echo "$file"
      #     echo "$xfilename"
      #     # echo 038611608639.dkr.ecr.us-east-1.amazonaws.com/$xfilename:release
      #     echo $repo/$xfilename:release
      #     docker build -t $xfilename -f $file --no-cache .
      #     docker tag $xfilename $repo/$xfilename:release
      #     docker push $repo/$xfilename:release
      fi
    fi
  done
done