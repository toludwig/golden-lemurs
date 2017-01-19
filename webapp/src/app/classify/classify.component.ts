import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { json } from 'd3';
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
  @Input() repo: string = 'https://github.com/InformatiCup/InformatiCup2017';
  @Output() fetching = false;
  @Output() result = new EventEmitter<Repo>();
  regex = /^https?:\/\/github.com\/(.+)\/(.+)$/;
  api = (name, title) => `http://localhost:8081/rate/${name}/${title}/`;
  constructor(private repositories: RepositoryService) { }

  ngOnInit() {
  }

  public classify() {
    let [name, title] = this.regex.exec(this.repo).slice(1);
    console.log(`testing: ${this.api(name, title)}`);
    this.fetching = true;
    json(this.api(name, title), (response: Repo) => {
        this.fetching = false;
        this.repositories.save(`https://github.com/${name}/${title}`, response);
        this.result.emit(response);
    });
  }
  public repoValid(): boolean {
    return this.repo.match(this.regex) != null;
  }

}
