import { Component, AfterViewInit, ViewChild } from '@angular/core';
import * as d3 from 'd3';

// TODO: fill dat shit, enhance & modify
export type Architecture = Network[];
export interface Network {
  name: string;
  layers: Layer[];
  input: string;
  output: string;
}
export interface Layer {
  neurons: Neuron[];
  prev: Layer | "input";
  next: Layer | "output";
}
export interface Neuron {
  weight: number;
  inputs: Neuron[] | number[];
  output: number;
}


@Component({
  selector: 'app-network',
  templateUrl: './network.component.html',
  styleUrls: ['./network.component.css']
})
export class NetworkComponent implements AfterViewInit {

  @ViewChild('net') public net;
  repo = 'https://github.com/mschuwalow/StudDP'; // TODO: map to url
  architecture = [
    {
      name: 'sample',
      layers: [
        {
          neurons: [
            {
              weight: 42,
              inputs: [1, 3, 3, 7],
              output: 23
            }, {
              weight: 666,
              inputs: [13],
              output: 3.1415
            }
          ],
          prev: 'input',
          next: 'output'
        }],
      input: 'foo',
      output: 'bar'
    }
  ] as Architecture;
  constructor() { }

  ngAfterViewInit() {
    let elem = this.net.nativeElement;

    const networkCoordinates = [ [0, 0] ];
    const networks = d3.select(elem)
      .selectAll('g.network').data(this.architecture)
      .enter().append('g')
      .classed('network', true)
      .attr('transform', (network, i) => {
          return `translate(${networkCoordinates[i][0]}, ${networkCoordinates[i][1]})`;
      });
    networks.selectAll('rect.layer'); // this is important

      // TODO: continue
      //networks.sel
  }

}
