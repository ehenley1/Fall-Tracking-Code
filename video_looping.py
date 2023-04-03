import os
import subprocess
from argparse import ArgumentParser

os.chdir("C:/Users/lazyp/mmpose")

def main():
    #Arguments to be submitted to run the top_down_pose_estimation script
    parser = ArgumentParser()
    parser.add_argument('--video-path', type=str, help='Video path')
    parser.add_argument(
        '--show',
        action='store_true',
        default=False,
        help='whether to show visualizations.')
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

    #Location where videos exist
    video_directory = "C:/Users/lazyp/Fall_Tracker/Videos/video1.mp4"
    #Array of video names in the directory
    #video_names = ["video1.mp4", "video2.mp4"]
    #Estimation script location
    top_down_pose_estimation = "demo/top_down_video_demo_with_mmdet.py"
    #det_config file
    det_config = "demo/mmdetection_cfg/faster_rcnn_r50_fpn_coco.py "
    #det_checkpoint file
    det_checkpoint = "https://download.openmmlab.com/mmdetection/v2.0/faster_rcnn/faster_rcnn_r50_fpn_1x_coco/faster_rcnn_r50_fpn_1x_coco_20200130-047c8118.pth"
    #pose_config file
    pose_config = "configs/body/2d_kpt_sview_rgb_vid/posewarper/posetrack18/hrnet_w48_posetrack18_384x288_posewarper_stage2.py "
    #pose_checkpoint file
    pose_checkpoint = "https://download.openmmlab.com/mmpose/top_down/posewarper/hrnet_w48_posetrack18_384x288_posewarper_stage2-4abf88db_20211130.pth"
    #output_path
    output_path = "C:/Users/lazyp/Fall_Tracker"
    
    #loop joining together video names and locations to perform top_down_pose_estimation
    #for video_name in video_names:
        #video_path = os.path.join(video_directory, video_name)
       # output_path = os.path.join(video_directory, video_name.replace(".mp4", ".json"))
    subprocess.run(["python", top_down_pose_estimation, det_config, det_checkpoint, pose_config, pose_checkpoint,
                        "--video-path", video_directory,
                        "--out-video-root", output_path,
                        "--use-multi-frames",
                        "--online"],
                       capture_output=True)


if __name__ == '__main__':
    main()
