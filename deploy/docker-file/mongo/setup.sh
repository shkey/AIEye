#!/bin/bash
mongo <<EOF
use admin;
db.auth('root', '123456');
use AIEye;
db.createUser({user:'aieye',pwd:'123456',roles:[{role:'readWrite',db:'AIEye'}]});
EOF
