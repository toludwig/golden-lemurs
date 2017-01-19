import { Injectable } from '@angular/core';
import { Repo } from './repo/repo.component';

@Injectable()
export class RepositoryService {

  constructor() { }
  private urls: string[] = [];
  private repos: Repo[] = [];

  public save(url: string, repo: Repo) {
    this.urls.push(url);
    this.repos.push(repo);
  }
  public get(url: string): Repo {
    let i = this.urls.findIndex(value => value.toLowerCase() == url.toLowerCase());
    if (i == -1) {
      return null;
    } else {
      return this.repos[i];
    }
  }

  public getLatest(): Repo {
    if (this.repos.length == 0)
      return null;
    else
      return this.repos[this.repos.length - 1];
  }

}
