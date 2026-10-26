import test from 'node:test';
import assert from 'node:assert/strict';
import {sceneClock,frameAtSeconds,progressAt,motionTime,randomFor,project2D} from '../assets/frame-clock.mjs';

test('absolute subtitles and Sequence-local frames map to the same instant', () => {
  const t=sceneClock(79,25,50);assert.equal(t.localFrame,29);assert.equal(t.localSeconds + 50/25,t.absoluteSeconds);assert.equal(frameAtSeconds(t.absoluteSeconds,25),79);
});
test('seconds use the actual composition fps, including noninteger fps',()=>{
  assert.equal(frameAtSeconds(1,24),24);assert.equal(frameAtSeconds(1,30),30);assert.equal(frameAtSeconds(2,29.97),60);
});
test('frame seeking does not depend on render order or earlier calls',()=>{
  function draw(f){const {localSeconds}=sceneClock(f,30,15);return {x:120*localSeconds,ink:progressAt(f,15,45),jitter:randomFor('fixture','stroke-A')};}
  const expected=draw(41);[200,0,40,90,15].map(draw);assert.deepEqual(draw(41),expected);
});
test('each stable object keeps its own variation across frames',()=>{
  const a=randomFor('paper','fibre-1');for(let i=0;i<20;i++)assert.equal(randomFor('paper','fibre-1'),a);assert.notEqual(a,randomFor('paper','fibre-2'));
});
test('character motion can step while camera clock remains continuous',()=>{
  assert.equal(motionTime(1,24,12),0);assert.equal(motionTime(2,24,12),1/12);assert.notEqual(sceneClock(1,24).absoluteSeconds,sceneClock(0,24).absoluteSeconds);
});
test('world-space marker and subject share transformed coordinates',()=>{
  const p={x:10,y:20},camera={x:4,y:8,scale:2,angle:Math.PI/2},viewport={width:100,height:80};
  const q=project2D(p,camera,viewport);assert.ok(Math.abs(q.x-26)<1e-10);assert.ok(Math.abs(q.y-52)<1e-10);
  const moved=project2D(p,{...camera,x:5},viewport);assert.notDeepEqual(moved,q);
});
test('invalid frame/clock and zero-duration inputs stop instead of NaN frames',()=>{
  assert.throws(()=>sceneClock(1,0));assert.throws(()=>sceneClock(1.5,30));assert.throws(()=>progressAt(1,0,0));assert.throws(()=>frameAtSeconds(NaN,24));assert.throws(()=>project2D({x:0,y:0},{x:0,y:0,scale:0},{width:10,height:10}));
});
