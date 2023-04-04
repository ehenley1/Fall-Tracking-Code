#Test Cases for top_down_pose_estimation loop
import os
import cv2
import mmcv
import warnings
import subprocess
from argparse import ArgumentParser
os.chdir("C:/Users/lazyp/mmpose")
#Set up arguments
def main():

    parser = ArgumentParser()
    parser.add_argument('--video-path', type=str, help='Video path')
    parser.add_argument(
            '--show',
            action = 'store_true',
            help = 'whether to show visualizations')
    parser.add_argument(
        '--out-video-root',
        default='',
        help='Root of the output video file. '
        'Default not saving the visualization video.')
    parser.add_argument(
        '--use-multi-frames',
        action='store_true',
        default=False,
        help='whether to use multi frames for inference in the pose'
        'estimation stage. Default: False.')
    parser.add_argument(
        '--online',
        action='store_true',
        default=False,
        help='inference mode. If set to True, can not use future frame'
        'information when using multi frames for inference in the pose'
        'estimation stage. Default: False.')
    
    args = parser.parse_args()

    #Estimation, config, checkpoint, pose, checkpoint
    estimation_script = 'C:/Users/lazyp/Fall_Tracker/top_down_pose_estimation.py'
    assert os.path.exists(estimation_script), f"Estimation script is  not accessible"
    assert os.access(estimation_script, os.R_OK), f"Estimation script is not readible"

    det_config = "demo/mmdetection_cfg/faster_rcnn_r50_fpn_coco.py"
    assert os.path.exists(det_config), f"det_config is not accessible"
    assert os.access(det_config, os.R_OK), f"det_config is not readible"

    det_checkpoint = 'https://download.openmmlab.com/mmdetection/v2.0/faster_rcnn/faster_rcnn_r50_fpn_1x_coco/faster_rcnn_r50_fpn_1x_coco_20200130-047c8118.pth'

    pose_config = 'configs/body/2d_kpt_sview_rgb_vid/posewarper/posetrack18/hrnet_w48_posetrack18_384x288_posewarper_stage2.py'
    assert os.path.exists(pose_config), f"pose_config is not accessible"
    assert os.access(pose_config, os.R_OK), f"pose_config is not readible"

    pose_checkpoint = 'https://download.openmmlab.com/mmpose/top_down/posewarper/hrnet_w48_posetrack18_384x288_posewarper_stage2-4abf88db_20211130.pth'
    
    #Videos to run tests on

    video1 = 'C:/Users/lazyp/Fall_Tracker/Videos/video1.mp4'  #This video is low resolution with a far away target
    assert os.path.exists(video1), f"Video1 is  not accessible"
    assert os.access(video1, os.R_OK), f"Video1 is not readible"

    video2 = 'C:/Users/lazyp/Fall_Tracker/Videos/video3.mp4' #This video is mid resolution, spins into a fall
    assert os.path.exists(video2), f"Video2 is  not accessible"
    assert os.access(video2, os.R_OK), f"Video2 is not readible"

    video3 = 'C:/Users/lazyp/Fall_Tracker/Videos/video4.mp4' #This video is high resolution, very slow spin
    assert os.path.exists(video3), f"Video3 is  not accessible"
    assert os.access(video3, os.R_OK), f"Video3 is not readible"

    video4 = 'C:/Users/lazyp/Fall_Tracker/Videos/video1.mp4' #This video is mid resolution, cleanest fall
    assert os.path.exists(video4), f"Video4 is  not accessible"
    assert os.access(video4, os.R_OK), f"Video4 is not readible"

#Test for video 1


