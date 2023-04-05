import os
import warnings
from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('det_config', help='Config file for detection')
    parser.add_argument('det_checkpoint', help='Checkpoint file for detection')
    parser.add_argument('pose_config', help='Config file for pose')
    parser.add_argument('pose_checkpoint', help='Checkpoint file for pose')
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
        '--device', default='cuda:0', help='Device used for inference')
    parser.add_argument(
        '--det-cat-id',
        type=int,
        default=1,
        help='Category id for bounding box detection model')
    parser.add_argument(
        '--bbox-thr',
        type=float,
        default=0.3,
        help='Bounding box score threshold')
    parser.add_argument(
        '--kpt-thr', type=float, default=0.3, help='Keypoint score threshold')
    parser.add_argument(
        '--radius',
        type=int,
        default=4,
        help='Keypoint radius for visualization')
    parser.add_argument(
        '--thickness',
        type=int,
        default=1,
        help='Link thickness for visualization')
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
    return args
    
def main():
    import cv2
    import mmcv
    import pandas as pd
    from mmpose.apis import (collect_multi_frames, inference_top_down_pose_model,
                             init_pose_model, process_mmdet_results,
                             vis_pose_result)
    from mmpose.datasets import DatasetInfo
    try:
        from mmdet.apis import inference_detector, init_detector
        has_mmdet = True
    except (ImportError, ModuleNotFoundError):
        has_mmdet = False
    args = parse_args()
    
    """Visualize the demo video (support both single-frame and multi-frame). Using mmdet to detect the human.
    """
    assert has_mmdet, 'Please install mmdet to run the demo.'
    assert args.show or (args.out_video_root != '')
    assert args.det_config is not None
    assert args.det_checkpoint is not None

    print('Initializing model...')
    # build the detection model from a config file and a checkpoint file
    det_model = init_detector(
        args.det_config, args.det_checkpoint, device=args.device.lower())
    # build the pose model from a config file and a checkpoint file
    pose_model = init_pose_model(
        args.pose_config, args.pose_checkpoint, device=args.device.lower())
    dataset = pose_model.cfg.data['test']['type']
    # get datasetinfo
    dataset_info = pose_model.cfg.data['test'].get('dataset_info', None)
    if dataset_info is None:
        warnings.warn(
            'Please set `dataset_info` in the config.'
            'Check https://github.com/open-mmlab/mmpose/pull/663 for details.',
            DeprecationWarning)
    else:
        dataset_info = DatasetInfo(dataset_info)
    # read video
    video = mmcv.VideoReader(args.video_path)
    assert video.opened, f'Faild to load video file {args.video_path}'

    if args.out_video_root == '':
        save_out_video = False
    else:
        os.makedirs(args.out_video_root, exist_ok=True)
        save_out_video = True

    if save_out_video:
        fps = video.fps
        size = (video.width, video.height)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        videoWriter = cv2.VideoWriter(
            os.path.join(args.out_video_root,
                         f'vis_{os.path.basename(args.video_path)}'), fourcc,
            fps, size)

    # frame index offsets for inference, used in multi-frame inference setting
    if args.use_multi_frames:
        assert 'frame_indices_test' in pose_model.cfg.data.test.data_cfg
        indices = pose_model.cfg.data.test.data_cfg['frame_indices_test']

    # whether to return heatmap, optional
    return_heatmap = False

    # return the output of some desired layers,
    # e.g. use ('backbone', ) to return backbone feature
    output_layer_names = None

    # making an empty list to store each dataframe
    frame_list = []

    print('Running inference...')
    frame_list = []
    for frame_id, cur_frame in enumerate(mmcv.track_iter_progress(video)):
        det_results = process_mmdet_results(inference_detector(det_model, cur_frame), args.det_cat_id)
        multi_frames = collect_multi_frames(video, frame_id, indices, args.online) if args.use_multi_frames else cur_frame
        pose_results = inference_top_down_pose_model(
            pose_model,
            multi_frames,
            det_results,
            bbox_thr=args.bbox_thr,
            format='xyxy',
            dataset=dataset,
            dataset_info=dataset_info,
            return_heatmap=False,
            outputs=None
    )

    if pose_results:
        frame_list.append(pd.DataFrame(pose_results[0]['keypoints']))

        # show the results
        vis_frame = vis_pose_result(
            pose_model,
            cur_frame,
            pose_results,
            dataset=dataset,
            dataset_info=dataset_info,
            kpt_score_thr=args.kpt_thr,
            radius=args.radius,
            thickness=args.thickness,
            show=False)
        
        # Extract the 2D keypoints from the result and save them to a file
        #print(pose_results[0].keys())
        keypoints = pose_results[0]['keypoints']
        #out.write(keypoints)
        #print(keypoints)
        
        falldata1= pd.DataFrame(keypoints)
        frame_list.append(falldata1)
        final_list = pd.concat(frame_list, keys=range(len(frame_list)))


        #dffall=falldata1.concat({'falldata1':'Frame'},axis=0,join='outer',ignore_index=False,keys=None,levels=None,verify_integrity=False,sort=False,copy=True)
        #dffall=falldata1.append({'falldata1':'Frame'},ignore_index=True)
        #keypoints_file = open('keypoints.xlsx', 'a')
        #keypoints_file.write(f'Frame {video.frame_num}:\n{keypoints}\n\n')
        #keypoints_file.close()

        if args.show:
            cv2.imshow('Frame', vis_frame)

        if save_out_video:
            videoWriter.write(vis_frame)
            #falldata1.to_excel('dffall.xlsx', index=False)

        #if args.show and cv2.waitKey(1) & 0xFF == ord('q'):
            #break

    final_list.to_json('testtesttest.json')

    if save_out_video:
        videoWriter.release()
    if args.show:
        cv2.destroyAllWindows()
        video.release()

if __name__ == '__main__':
    main()
