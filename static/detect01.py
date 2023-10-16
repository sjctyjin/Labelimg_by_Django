import torch
import numpy as np
import cv2
import time
import os
# model = torch.hub.load('yolov5', 'custom', path='yolov5/runs/train/exp15/weights/last.pt',source='local')
model = torch.hub.load('yolov5', 'custom', path='usermodel/jim/20230817_111716-cucumber_5_Maturity/cucumber_5_Maturity/weights/best.pt',source='local')

img_path = 'userdata/jim/20230817_140728-cucumber_5_Maturity/images/'

label_class = {}


for i in os.listdir(img_path):

    frame = cv2.imread(f'userdata/jim/20230817_140728-cucumber_5_Maturity/images/{i}')
    start = time.time()
    results = model(frame)
    print(frame.shape[:2])
    YOLO_Format = ""
    xml_content = f"""
                      <annotation>
                          <folder>images</folder>
                          <filename>{i}</filename>
                          <path>path</path>
                          <source>
                              <database>Unknown</database>
                          </source>
                          <size>
                              <width>{frame.shape[1]}</width>
                              <height>{frame.shape[0]}</height>
                              <depth>3</depth>
                          </size>
                          <segmented>0</segmented>
                      """

    if len(results.pandas().xyxy[0]) > 0:
        #
        # print("="*30)
        # print(results.pandas().xyxy[0])
        # print(results.pandas().xyxy[0]["confidence"])#信心值
        # print(results.pandas().xyxy[0]["confidence"][0])#信心值
        # print("=" * 30)

        for i in range(len(results.pandas().xyxy[0])):

            print("label : ",results.pandas().xyxy[0])
            x = int(results.pandas().xyxy[0]["xmin"][i])
            y = int(results.pandas().xyxy[0]["ymin"][i])
            w = int(results.pandas().xyxy[0]["xmax"][i])
            h = int(results.pandas().xyxy[0]["ymax"][i])
            confi = int(results.pandas().xyxy[0]["confidence"][i]*100)
            names_label = results.pandas().xyxy[0]["name"][i]
            label_class[results.pandas().xyxy[0]["class"][i]] = names_label
            # crop_img = frame[x:x + w,y:y + h]

            print(x,y)
            print(h,w)
            if confi > 10:
                # frame[y:h, x:w] = np.zeros(frame[y:h, x:w].shape, dtype='uint8')
                crop_img = frame[y:h, x:w]
                cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 5)


                cv2.circle(frame, (int((w+x)/2),int((y+h)/2)),2, (255, 0, 0), -1)

                font = cv2.FONT_HERSHEY_COMPLEX
                cv2.putText(frame, f'{names_label}_{confi}%', (x+10, y+10), font, 1, (255,255,255), 1, cv2.LINE_AA)
                cv2.putText(frame, f'X : {int((w+x)/2)},Y:{int((y+h)/2)}', (int((w+x)/2)+10, int((y+h)/2)+10), font, 1, (255,255,255), 1, cv2.LINE_AA)

                xml_content += f"""<object>
                            <name>{names_label}</name>
                            <pose>Unspecified</pose>
                            <truncated>0</truncated>
                            <difficult>0</difficult>
                            <bndbox>
                                <xmin>{x}</xmin>
                                <ymin>{y}</ymin>
                                <xmax>{w}</xmax>
                                <ymax>{h}</ymax>
                            </bndbox>
                        </object>
                        """
                    # for a in range(0,10):
                    #     print("=" * a)
                    # print(round(float(imgwidth),1),round(float(imgheight),1))

                ymin, xmin, ymax, xmax, image_w, image_h = [y,x,
                                                            h,w,
                                                            frame.shape[1],
                                                            frame.shape[0]]
                (x_iw_ratio, y_ih_ratio) = (
                ((xmin + xmax) * 0.5) / image_w, ((ymin + ymax) * 0.5) / image_h)
                tw_iw_ratio = (xmax - xmin) * 1. / image_w
                th_ih_ratio = (ymax - ymin) * 1. / image_h
                YOLO_Format += f"""{ results.pandas().xyxy[0]["class"][i]} {round(x_iw_ratio, 6)} {round(y_ih_ratio, 6)} {round(tw_iw_ratio, 6)} {round(th_ih_ratio, 6)}\n"""

                xml_content += "</annotation>"
    else:
        print("沒東西")
    # cv2.imshow('YOLO COCO 01', np.squeeze(results.render()))
    print("XML_Format : ",xml_content)
    print("YOLO_Format : ",YOLO_Format)
    print(sorted(label_class.items()))
    ended = time.time()
    sec = ended - start
    fps = 1 / sec
    # print('FPS: {:5.2f}'.format(n / (time.time() - begin_time)))
    # text = 'FPS: {:5.2f}'.format(n / (time.time() - begin_time))
    text = 'fps = {:5.2f}'.format(fps)
    cv2.putText(frame, text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 23, 0), 1, cv2.LINE_AA)
    cv2.imshow('YOLO COCO 01', frame)
    # print("~"*50)

    # if len(results.pandas().xyxy[0]) > 0:
    #     if confi > 60:
    #         cv2.imshow('YOLO COCO 02', crop_img)
    #
    # else:
    #     cv2.destroyWindow('YOLO COCO 02')
    # out.write(frame)  # 將取得的每一幀圖像寫入空的影片
    cv2.waitKey(0)


