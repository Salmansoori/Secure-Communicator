# Secure-Communicator

1.) A web-based secure chat application with advanced end-to-end encryption.<br/>
2.) Integrated with face recognition as a 2-Factor authentication (2FA).<br/>
3.) Android application is also available for the same at this link <br/> 
(https://github.com/akhil2000mittal/encryp_chat)

# First run these commands

Download mini-conda and use conda environment for easy installation<br/>
pip install opencv-python<br/>
conda install -c conda-forge dlib<br/>
pip install face_recognition<br/>


# First server setup 
FLASK_APP=app.py 
*** Create new conda environment ***
conda create --name secure python=3
conda activate secure   (else bydefault set the:: env export FLASK_ENV=development)

# Run Command
python app.py


#If need to run using flask else try to avoid this path.


flask run --host=ec2-3-137-222-118.us-east-2.compute.amazonaws.com --port=8080 
*** In Debug Mode ***
FLASK_DEBUG=1 flask run --host=ec2-3-137-222-118.us-east-2.compute.amazonaws.com --port=8080
