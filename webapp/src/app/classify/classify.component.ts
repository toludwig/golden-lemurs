import { Component, ViewChild, OnInit, Input, Output, EventEmitter } from '@angular/core';
import * as d3 from 'd3';
import { Repo } from '../repo/repo.component';
import { RepositoryService } from '../repository.service';


@Component({
  selector: 'app-classify',
  templateUrl: './classify.component.html',
  styleUrls: ['./classify.component.css']
})
export class ClassifyComponent implements OnInit {

  input = 'Enter a github repo url';
  action = 'Classify me!';
  @ViewChild('rating') rating;
  @Input() repo: string = 'https://github.com/InformatiCup/InformatiCup2017';
  @Input() minimal: boolean;
  @Output() fetching = false;
  @Output() result = new EventEmitter<Repo>();
  regex = /^https?:\/\/github.com\/(.+)\/(.+)$/;
  api = (name, title, min) => `http://localhost:8081/rate/${name}/${title}/${min ? 1 : 0}`;
  constructor(private repositories: RepositoryService) { }

  ngOnInit() {
  }

  public classify() {
    let [name, title] = this.regex.exec(this.repo).slice(1);
    this.fetching = true;
    d3.json(this.api(name, title, this.minimal), (response: Repo) => {
      this.fetching = false;
      this.result.emit(response);
    });
  }
  public repoValid(): boolean {
    return this.repo.match(this.regex) != null;
  }

}
