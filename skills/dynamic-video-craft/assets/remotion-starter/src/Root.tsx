import React from 'react';
import {Composition} from 'remotion';
import {Video} from './Video';
import config from './video.json';

export const Root: React.FC = () => (
  <Composition
    id="DynamicVideo"
    component={Video}
    width={config.width}
    height={config.height}
    fps={config.fps}
    durationInFrames={Math.round(config.duration * config.fps)}
    defaultProps={{music: true}}
  />
);
