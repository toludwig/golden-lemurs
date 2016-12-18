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
    },
    {
      name: 'sample2',
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
        },
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
        }
      ],
      input: 'foo',
      output: 'bar'
    }
  ] as Architecture;
  constructor() { }

  ngAfterViewInit() {
    let elem = this.net.nativeElement;

    function sum(list: Array<number>) {
      return list.reduce((last, curr) => last + curr, 0);
    }
    function cumsum(list: Array<number>, index) {
      if (index == 0) return 0;
      return list.reduce((last, curr, i) => (i < index ? last + curr : last), 0);
    }

    function size(obj, level: number, dimension: 'x' | 'y'): number {
      switch (level) {
        case 0: // neuron
          return 10;
        case 1: // layer
          if (dimension == 'x')
            return sum((obj as Layer).neurons.map(n => size(n, level - 1, dimension))) * 1.1;
          else
            return 30;
        case 2: // network
          if (dimension == 'y')
            return Math.max(...(obj as Network).layers.map(n => size(n, level - 1, dimension))) * 1.1 + 20;
          else
            return sum((obj as Network).layers.map(n => size(n, level - 1, dimension))) * 1.1 + 10;
      }
    }

    const netXSize = this.architecture.map(n => size(n, 2, 'x'));
    const netYSize = this.architecture.map(n => size(n, 2, 'y'));
    const netX = netXSize.map((_, i) => 0); //cumsum(netXSize, i));
    const netY = netYSize.map((_, i) => cumsum(netYSize, i));

    let svg = d3.select(elem)
      .attr('width', 1000)
      .attr('height', 600);
    let g = svg.append('g');
    svg.call(d3.zoom().scaleExtent([1 / 8, 16])
      .on('zoom', function() { g.attr('transform', d3.event.transform); }));
    let networks = g.selectAll('g.network').data(this.architecture);
    networks = networks.enter().append('g')
      .classed('network', true)
      .merge(networks)
      .attr('transform', (network, i) => {
        return `translate(${netX[i]}, ${netY[i]})`;
      });
    networks
      .append('text')
      .attr('x', 0)
      .attr('y', -10)
      .attr('font-size', 10)
      .text(network => network.name);
    networks
      .append('text')
      .attr('font-size', 10)
      .attr('x', -20)
      .attr('y', 15)
      .text(network => network.input);
    networks
      .append('text')
      .attr('x', n => size(n, 2, 'x'))
      .attr('y', 15)
      .attr('font-size', 10)
      .text(network => network.output);

    let myLayers = d3.local();
    let layers = networks.selectAll('g.layer').data(function (network) {
      myLayers.set(this as Element, network.layers.map(l => size(l, 1, 'x')));
      return network.layers;
    });
    layers = layers.enter().append('g')
      .classed('layer', true)
      .merge(layers)
      .attr('transform', function (layer, i) {
        let layers = myLayers.get(this as Element) as number[];
         return `translate(${cumsum(layers, i) * 1.2 }, 0)`;
    } );
    layers
      .append('rect')
      .attr('width', l => size(l, 1, 'x'))
      .attr('height', l => size(l, 1, 'y'))
      .attr('x', 0)
      .attr('y', 0)
      .attr('fill-opacity', '0')
      .attr('stroke-width', '2')
      .attr('stroke', 'black');

    let neurons = layers.selectAll('circle.neuron').data(layer => layer.neurons);
    neurons.enter().append('circle')
      .classed('neuron', true)
      .merge(neurons)
      .attr('cx', d => size(d, 0, 'x') * 1.2)
      .attr('cy', (d, i) => (i + 1) * size(d, 0, 'x') * 1.1)
      .attr('r', n => size(n, 0, 'x') / 2)
      .attr('fill-opacity', '0')
      .attr('stroke-width', '1')
      .attr('stroke', 'black')
    let weights = layers.selectAll('text.neuron').data(layer => layer.neurons);
    weights.enter().append('text')
      .text(neuron => `${neuron.weight}`)
      .attr('font-size', d => size(d, 0, 'x') * 0.5)
      .attr('text-anchor', 'middle')
      .attr('x', d => size(d, 0, 'x') * 1.2)
      .attr('y', (d, i) => (i + 1) * size(d, 0, 'x') * 1.2);
  }

}
