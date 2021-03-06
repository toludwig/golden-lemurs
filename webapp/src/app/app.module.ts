import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { RouterModule, Routes } from '@angular/router';

import { MaterialModule } from '@angular/material';

import { AppComponent } from './app.component';
import { ClassifyComponent} from './classify/classify.component';
import { DocsComponent } from './docs/docs.component';
import { NetworkComponent } from './network/network.component';
import { DataComponent } from './data/data.component';

import { RepoComponent } from './repo/repo.component';
import { TensorboardComponent } from './tensorboard/tensorboard.component';
import { RepositoryService } from './repository.service';

const routes = [
  { path: '', pathMatch: 'full', redirectTo: 'classify' },
  { path: 'classify', component: ClassifyComponent },
  { path: 'docs/:page', component: DocsComponent },
  { path: 'dashboard', component: NetworkComponent },
  { path: 'tensorboard', component: TensorboardComponent },
  { path: 'data', component: DataComponent },
  { path: '**', component: ClassifyComponent }
];

@NgModule({
  declarations: [
    AppComponent,
    ClassifyComponent,
    DocsComponent,
    NetworkComponent,
    DataComponent,
    RepoComponent,
    TensorboardComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpModule,
    RouterModule.forRoot(routes),
    MaterialModule.forRoot()
  ],
  providers: [RepositoryService],
  bootstrap: [AppComponent]
})
export class AppModule { }
