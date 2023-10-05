# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

## [0.6.0] - 2023/10/05

### Changed

- Constant page_limit across all calls.

## [0.5.0] - 2023/10/02

### Changed

- Retry on page creation

## [0.4.0] - 2023/08/24

### Changed

- property update methods

## [0.3.0] - 2023/08/07

### Fixed

- Avoid getting page on page creation

## [0.2.0] - 2023/07/14

### Fixed

- undefined last_prop
- Overwrite option overwrites existing file instead of creating a new one

## [0.1.0] - 2023/06/22

### Added

- support for unique ID property
- Initialisation for RollupPropertyValue and RollupFilter
- Status filter
- Overwrite flag to add_media
- Add option to create folders in GDrive
- Option for downloading spreadsheets from and uploading image to google drive
- Alive property for pages
- Add CheckboxFilter to init
- More block types
- Property Iterators

### Fixed

- PeopleFilter typo
- Merge create_folder and upload_file into add_media
- Error retrieving RichText if there is a URL in the text

### Changed

- Allow retry for post methods when getting data
- Rollup iterators, rollup filter and rollup values
- Query logic
- Change misleading message when a property doesn't exist


