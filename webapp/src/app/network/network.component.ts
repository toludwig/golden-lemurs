import { Component, AfterViewInit, ViewChild, Output, EventEmitter } from '@angular/core';

import { NETWORK } from './architecture';
import { Repo } from './../repo/repo.component';

@Component({
  selector: 'app-network',
  templateUrl: './network.component.html',
  styleUrls: ['./network.component.css']
})
export class NetworkComponent implements AfterViewInit {

  @Output() public dashboard = NETWORK;

  repo = new EventEmitter<Repo>(); // TODO: map to url
  constructor() { }

  ngAfterViewInit() {
      console.dir(this.dashboard);

    // [1] DEV [2] HW [3] EDU [4] DOCS [5] WEB [6] DATA [7] OTHER
    const DEV = 1, HW = 2, EDU = 3, DOCS = 4, WEB = 5, DATA = 6, OTHER = 7;
    const NAMES = ["DEV", "HW", "EDU", "DOCS", "WEB", "DATA", "OTHER"];

    interface NetworkDebugger {
      // CONVENIENCE
      names: string[]; // map numbers to category names
      // NETWORK DATA
      decision: number;
      // CNN
      softmaxCNN: number[];
      outputCNN: number;
      filtersCNN: number[]; // filter sizes as in settings.py

      // parameters
      sequenceLength: number;
      embeddingSize: number;
      // FFN

      // INPUT DATA
      readme: string;
      readmePreprocessed: string;
      contributors: number;
      issues: number;
      branches: number;
      forks: number;
      stars: number;
      pullRequests: number;
      subscribers: number;
      commits: number;
      // as unix time
      commitTimes: number[];
      startTime: number;
      updateTime: number;
    }
    let data = {

    }; // TODO suck it out of maxim
  }

}
