import cv2
import face_recognition
import pickle
import os
from imutils import paths


def capture(user_name):
    camera = cv2.VideoCapture(0)
    print("Press 'q' to capture when READY!!!")
    while True:
        return_value, image = camera.read()
        cv2.imshow('frame', image)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            del camera
            return save_image(image, user_name)


def save_image(image, user_name):
    cv2.imwrite(r'image_database/{}.png'.format(user_name), image)


def data_enc_update():
    # Folder name is Images
    image_paths = list(paths.list_images('image_database'))
    known_encodings = []
    known_names = []

    for (i, img_path) in enumerate(image_paths):
        # Reading file name and loading image in RGB.
        file_name = img_path.split(os.path.sep)[1].split(".")[0]
        image = cv2.imread(img_path)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Use face_recognition to locate faces
        boxes = face_recognition.face_locations(rgb, model='hog')

        # Computing facial encoding
        encodings = face_recognition.face_encodings(rgb, boxes)
        for encoding in encodings:
            known_encodings.append(encoding)
            known_names.append(file_name)
    # print(known_names)
    # User facial data dictionary
    user_data = {
        "encodings": known_encodings,
        "names": known_names
    }

    # Writing data to files
    f = open("face_enc_user_database", "wb")
    f.write(pickle.dumps(user_data))
    f.close()


# noinspection SpellCheckingInspection
def verification(user_name):
    # Loading Model file
    # cascade_file = os.path.dirname(cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"
    # face_cascade = cv2.CascadeClassifier(cascade_file)

    # Loading user data file
    data = pickle.loads(open('face_enc_user_database', "rb").read())

    # Load saved/captured image of user
    im_path = r'image_database/{}.png'.format(user_name)
    image = cv2.imread(im_path)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # faces = face_cascade.detectMultiScale(gray,
    #                                       scaleFactor=1.1,
    #                                       minNeighbors=5,
    #                                       minSize=(60, 60),
    #                                       flags=cv2.CASCADE_SCALE_IMAGE)

    encodings = face_recognition.face_encodings(rgb)
    names = []

    for encoding in encodings:
        # Compare encodings with encodings in data["encodings"]
        # Matches contain array with boolean values and True for the embeddings it matches closely
        # and False for rest
        matches = face_recognition.compare_faces(data["encodings"],
                                                 encoding)
        name = "Unknown"    # By Default
        if True in matches:
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1
                name = max(counts, key=counts.get)

            # update the list of names
            names.append(name)
    return names


# # Only for testing
# if __name__ == '__main__':
#     import re
#     u_name = str(input("Enter username: ")).lower()
#     u_name = re.sub('[!@#$.<>?}{|=,:;\'"^&*(%)]', '', u_name)
#     # Register New user
#     capture(u_name)
#     # Updating database
#     data_enc_update()
#     # Verifying the SAME user here
#     verified_user = verification(u_name)
#     if len(verified_user) != 0:
#         print("Hello, {}".format(verified_user[0]))
#     else:
#         print("User not recognised")