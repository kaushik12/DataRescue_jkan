import $ from 'jquery'
import {chain, pick, omit, filter, defaults} from 'lodash'

import TmplListGroupItem from '../templates/list-group-item'
import {setContent, slugify, createDatasetFilters, collapseListGroup} from '../util'

export default class {
  constructor (opts) {
    // pagination setup
    this.itemsPerPage = 15;
    this.currentPage = 1;
    this.organizations = this._organizationsWithCount(opts.datasets, opts.params);
    
    this.renderPage();
    this.setupPagination();

    const organizations = this._organizationsWithCount(opts.datasets, opts.params)
    const organizationsMarkup = organizations.map(TmplListGroupItem)
    setContent(opts.el, organizationsMarkup)
    collapseListGroup(opts.el)
  }

  _organizationsWithCount (datasets, params) {
    return chain(datasets)
      .groupBy('organization')
      .map(function (datasetsInOrg, organization) {
        const filters = createDatasetFilters(pick(params, ['category']))
        const filteredDatasets = filter(datasetsInOrg, filters)
        const orgSlug = slugify(organization)
        const selected = params.organization && params.organization === orgSlug
        const itemParams = selected ? omit(params, 'organization') : defaults({organization: orgSlug}, params)
        return {
          title: organization,
          url: '?' + $.param(itemParams),
          count: filteredDatasets.length,
          unfilteredCount: datasetsInOrg.length,
          selected: selected
        }
      })
      .orderBy('unfilteredCount', 'desc')
      .value()
  }

  renderPage() {
    const start = (this.currentPage - 1) * this.itemsPerPage;
    const end = start + this.itemsPerPage;
    const paginatedItems = this.organizations.slice(start, end);
    
    const organizationsMarkup = paginatedItems.map(TmplListGroupItem);
    setContent('[data-hook="organizations-list"]', organizationsMarkup);
    this.updatePaginationControls();
  }

  setupPagination() {
    const paginationEl = document.querySelector(".pagination");
    paginationEl.addEventListener("click", (e) => {
      if (e.target.tagName === "A" && e.target.dataset.page) {
        e.preventDefault();
        const newPage = parseInt(e.target.dataset.page);
        if (newPage > 0 && newPage <= this.getTotalPages()) {
          this.currentPage = newPage;
          this.renderPage();
        }
      }
    });
  }

  updatePaginationControls() {
    const totalPages = this.getTotalPages();
    const paginationEl = document.querySelector(".pagination");

    let paginationMarkup = `
      <li class="page-item ${this.currentPage === 1 ? "disabled" : ""}">
        <a class="page-link" href="#" data-page="${this.currentPage - 1}">Previous</a>
      </li>`;

    for (let i = 1; i <= totalPages; i++) {
      paginationMarkup += `
        <li class="page-item ${this.currentPage === i ? "active" : ""}">
          <a class="page-link" href="#" data-page="${i}">${i}</a>
        </li>`;
    }

    paginationMarkup += `
      <li class="page-item ${this.currentPage === totalPages ? "disabled" : ""}">
        <a class="page-link" href="#" data-page="${this.currentPage + 1}">Next</a>
      </li>`;

    paginationEl.innerHTML = paginationMarkup;
  }

  getTotalPages() {
    return Math.ceil(this.organizations.length / this.itemsPerPage);
  }
}
