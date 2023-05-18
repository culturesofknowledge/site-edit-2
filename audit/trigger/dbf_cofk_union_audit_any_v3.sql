
create or replace function dbf_cofk_union_audit_any() returns trigger
    language plpgsql
as
$$
declare
  statement varchar(500);
begin

  if TG_RELNAME = 'cofk_union_comment' then

    -- cofk_union_comment 1. comment_id
    if TG_OP = 'DELETE' then
      perform dbf_cofk_union_audit_literal_delete( 'cofk_union_comment',
        old.comment_id::text,
        old.comment_id,
        old.comment,
        'comment_id',
        old.comment_id::text );
    end if;

    -- cofk_union_comment 2. comment
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_comment',
        new.comment_id::text,
        new.comment_id,
        new.comment,
        'comment',
        new.comment::text,
        old.comment::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_comment',
        new.comment_id::text,
        new.comment_id,
        new.comment,
        'comment',
        new.comment::text );
    end if;

  end if; -- End of cofk_union_comment

-------------------

  if TG_RELNAME = 'cofk_union_event' then

  end if; -- End of cofk_union_event

-------------------

  if TG_RELNAME = 'cofk_union_image' then

    -- cofk_union_image 1. image_id
    if TG_OP = 'DELETE' then
      perform dbf_cofk_union_audit_literal_delete( 'cofk_union_image',
        old.image_id::text,
        old.image_id,
        old.image_filename,
        'image_id',
        old.image_id::text );
    end if;

    -- cofk_union_image 2. image_filename
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_image',
        new.image_id::text,
        new.image_id,
        new.image_filename,
        'image_filename',
        new.image_filename::text,
        old.image_filename::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_image',
        new.image_id::text,
        new.image_id,
        new.image_filename,
        'image_filename',
        new.image_filename::text );
    end if;

    -- cofk_union_image 3. thumbnail
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_image',
        new.image_id::text,
        new.image_id,
        new.image_filename,
        'thumbnail',
        new.thumbnail::text,
        old.thumbnail::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_image',
        new.image_id::text,
        new.image_id,
        new.image_filename,
        'thumbnail',
        new.thumbnail::text );
    end if;

    -- cofk_union_image 4. can_be_displayed
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_image',
        new.image_id::text,
        new.image_id,
        new.image_filename,
        'can_be_displayed',
        new.can_be_displayed::text,
        old.can_be_displayed::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_image',
        new.image_id::text,
        new.image_id,
        new.image_filename,
        'can_be_displayed',
        new.can_be_displayed::text );
    end if;

    -- cofk_union_image 5. display_order
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_image',
        new.image_id::text,
        new.image_id,
        new.image_filename,
        'display_order',
        new.display_order::text,
        old.display_order::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_image',
        new.image_id::text,
        new.image_id,
        new.image_filename,
        'display_order',
        new.display_order::text );
    end if;

    -- cofk_union_image 6. licence_details
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_image',
        new.image_id::text,
        new.image_id,
        new.image_filename,
        'licence_details',
        new.licence_details::text,
        old.licence_details::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_image',
        new.image_id::text,
        new.image_id,
        new.image_filename,
        'licence_details',
        new.licence_details::text );
    end if;

    -- cofk_union_image 7. licence_url
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_image',
        new.image_id::text,
        new.image_id,
        new.image_filename,
        'licence_url',
        new.licence_url::text,
        old.licence_url::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_image',
        new.image_id::text,
        new.image_id,
        new.image_filename,
        'licence_url',
        new.licence_url::text );
    end if;

    -- cofk_union_image 8. credits
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_image',
        new.image_id::text,
        new.image_id,
        new.image_filename,
        'credits',
        new.credits::text,
        old.credits::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_image',
        new.image_id::text,
        new.image_id,
        new.image_filename,
        'credits',
        new.credits::text );
    end if;

  end if; -- End of cofk_union_image

-------------------

  if TG_RELNAME = 'cofk_union_institution' then

    -- cofk_union_institution 1. institution_id
    if TG_OP = 'DELETE' then
      perform dbf_cofk_union_audit_literal_delete( 'cofk_union_institution',
        old.institution_id::text,
        old.institution_id,
        old.institution_name ||  case when old.institution_city > '' then ', ' || old.institution_city else '' end || case when old.institution_country > '' then ',' || old.institution_country else '' end,
        'institution_id',
        old.institution_id::text );
    end if;

    -- cofk_union_institution 2. institution_name
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_institution',
        new.institution_id::text,
        new.institution_id,
        new.institution_name ||  case when new.institution_city > '' then ', ' || new.institution_city else '' end || case when new.institution_country > '' then ',' || new.institution_country else '' end,
        'institution_name',
        new.institution_name::text,
        old.institution_name::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_institution',
        new.institution_id::text,
        new.institution_id,
        new.institution_name ||  case when new.institution_city > '' then ', ' || new.institution_city else '' end || case when new.institution_country > '' then ',' || new.institution_country else '' end,
        'institution_name',
        new.institution_name::text );
    end if;

    -- cofk_union_institution 3. institution_synonyms
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_institution',
        new.institution_id::text,
        new.institution_id,
        new.institution_name ||  case when new.institution_city > '' then ', ' || new.institution_city else '' end || case when new.institution_country > '' then ',' || new.institution_country else '' end,
        'institution_synonyms',
        new.institution_synonyms::text,
        old.institution_synonyms::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_institution',
        new.institution_id::text,
        new.institution_id,
        new.institution_name ||  case when new.institution_city > '' then ', ' || new.institution_city else '' end || case when new.institution_country > '' then ',' || new.institution_country else '' end,
        'institution_synonyms',
        new.institution_synonyms::text );
    end if;

    -- cofk_union_institution 4. institution_city
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_institution',
        new.institution_id::text,
        new.institution_id,
        new.institution_name ||  case when new.institution_city > '' then ', ' || new.institution_city else '' end || case when new.institution_country > '' then ',' || new.institution_country else '' end,
        'institution_city',
        new.institution_city::text,
        old.institution_city::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_institution',
        new.institution_id::text,
        new.institution_id,
        new.institution_name ||  case when new.institution_city > '' then ', ' || new.institution_city else '' end || case when new.institution_country > '' then ',' || new.institution_country else '' end,
        'institution_city',
        new.institution_city::text );
    end if;

    -- cofk_union_institution 5. institution_city_synonyms
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_institution',
        new.institution_id::text,
        new.institution_id,
        new.institution_name ||  case when new.institution_city > '' then ', ' || new.institution_city else '' end || case when new.institution_country > '' then ',' || new.institution_country else '' end,
        'institution_city_synonyms',
        new.institution_city_synonyms::text,
        old.institution_city_synonyms::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_institution',
        new.institution_id::text,
        new.institution_id,
        new.institution_name ||  case when new.institution_city > '' then ', ' || new.institution_city else '' end || case when new.institution_country > '' then ',' || new.institution_country else '' end,
        'institution_city_synonyms',
        new.institution_city_synonyms::text );
    end if;

    -- cofk_union_institution 6. institution_country
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_institution',
        new.institution_id::text,
        new.institution_id,
        new.institution_name ||  case when new.institution_city > '' then ', ' || new.institution_city else '' end || case when new.institution_country > '' then ',' || new.institution_country else '' end,
        'institution_country',
        new.institution_country::text,
        old.institution_country::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_institution',
        new.institution_id::text,
        new.institution_id,
        new.institution_name ||  case when new.institution_city > '' then ', ' || new.institution_city else '' end || case when new.institution_country > '' then ',' || new.institution_country else '' end,
        'institution_country',
        new.institution_country::text );
    end if;

    -- cofk_union_institution 7. institution_country_synonyms
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_institution',
        new.institution_id::text,
        new.institution_id,
        new.institution_name ||  case when new.institution_city > '' then ', ' || new.institution_city else '' end || case when new.institution_country > '' then ',' || new.institution_country else '' end,
        'institution_country_synonyms',
        new.institution_country_synonyms::text,
        old.institution_country_synonyms::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_institution',
        new.institution_id::text,
        new.institution_id,
        new.institution_name ||  case when new.institution_city > '' then ', ' || new.institution_city else '' end || case when new.institution_country > '' then ',' || new.institution_country else '' end,
        'institution_country_synonyms',
        new.institution_country_synonyms::text );
    end if;

  end if; -- End of cofk_union_institution

-------------------

  if TG_RELNAME = 'cofk_union_location' then

    -- cofk_union_location 1. location_id
    if TG_OP = 'DELETE' then
      perform dbf_cofk_union_audit_literal_delete( 'cofk_union_location',
        old.location_id::text,
        old.location_id,
        old.location_name,
        'location_id',
        old.location_id::text );
    end if;

    -- cofk_union_location 2. location_name
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'location_name',
        new.location_name::text,
        old.location_name::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'location_name',
        new.location_name::text );
    end if;

    -- cofk_union_location 3. latitude
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'latitude',
        new.latitude::text,
        old.latitude::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'latitude',
        new.latitude::text );
    end if;

    -- cofk_union_location 4. longitude
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'longitude',
        new.longitude::text,
        old.longitude::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'longitude',
        new.longitude::text );
    end if;

    -- cofk_union_location 5. location_synonyms
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'location_synonyms',
        new.location_synonyms::text,
        old.location_synonyms::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'location_synonyms',
        new.location_synonyms::text );
    end if;

    -- cofk_union_location 6. editors_notes
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'editors_notes',
        new.editors_notes::text,
        old.editors_notes::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'editors_notes',
        new.editors_notes::text );
    end if;

    -- cofk_union_location: placename element 1
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'element_1_eg_room',
        new.element_1_eg_room::text,
        old.element_1_eg_room::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'element_1_eg_room',
        new.element_1_eg_room::text );
    end if;

    -- cofk_union_location: placename element 2
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'element_2_eg_building',
        new.element_2_eg_building::text,
        old.element_2_eg_building::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'element_2_eg_building',
        new.element_2_eg_building::text );
    end if;

    -- cofk_union_location: placename element 3
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'element_3_eg_parish',
        new.element_3_eg_parish::text,
        old.element_3_eg_parish::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'element_3_eg_parish',
        new.element_3_eg_parish::text );
    end if;

    -- cofk_union_location: placename element 4
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'element_4_eg_city',
        new.element_4_eg_city::text,
        old.element_4_eg_city::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'element_4_eg_city',
        new.element_4_eg_city::text );
    end if;

    -- cofk_union_location: placename element 5
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'element_5_eg_county',
        new.element_5_eg_county::text,
        old.element_5_eg_county::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'element_5_eg_county',
        new.element_5_eg_county::text );
    end if;

    -- cofk_union_location: placename element 6
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'element_6_eg_country',
        new.element_6_eg_country::text,
        old.element_6_eg_country::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'element_6_eg_country',
        new.element_6_eg_country::text );
    end if;

    -- cofk_union_location: placename element 7
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'element_7_eg_empire',
        new.element_7_eg_empire::text,
        old.element_7_eg_empire::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_location',
        new.location_id::text,
        new.location_id,
        new.location_name,
        'element_7_eg_empire',
        new.element_7_eg_empire::text );
    end if;
  end if; -- End of cofk_union_location

-------------------

  if TG_RELNAME = 'cofk_union_manifestation' then

    -- cofk_union_manifestation 1. manifestation_id
    if TG_OP = 'DELETE' then
      perform dbf_cofk_union_audit_literal_delete( 'cofk_union_manifestation',
        old.manifestation_id,
        null,
        coalesce( old.id_number_or_shelfmark, '' ) || coalesce( old.printed_edition_details, '' ),
        'manifestation_id',
        old.manifestation_id::text );
    end if;

    -- cofk_union_manifestation 2. manifestation_type
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_type',
        new.manifestation_type::text,
        old.manifestation_type::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_type',
        new.manifestation_type::text );
    end if;

    -- cofk_union_manifestation 3. id_number_or_shelfmark
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'id_number_or_shelfmark',
        new.id_number_or_shelfmark::text,
        old.id_number_or_shelfmark::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'id_number_or_shelfmark',
        new.id_number_or_shelfmark::text );
    end if;

    -- cofk_union_manifestation 4. printed_edition_details
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'printed_edition_details',
        new.printed_edition_details::text,
        old.printed_edition_details::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'printed_edition_details',
        new.printed_edition_details::text );
    end if;

    -- cofk_union_manifestation 5. paper_size
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'paper_size',
        new.paper_size::text,
        old.paper_size::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'paper_size',
        new.paper_size::text );
    end if;

    -- cofk_union_manifestation 6. paper_type_or_watermark
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'paper_type_or_watermark',
        new.paper_type_or_watermark::text,
        old.paper_type_or_watermark::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'paper_type_or_watermark',
        new.paper_type_or_watermark::text );
    end if;

    -- cofk_union_manifestation 7. number_of_pages_of_document
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'number_of_pages_of_document',
        new.number_of_pages_of_document::text,
        old.number_of_pages_of_document::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'number_of_pages_of_document',
        new.number_of_pages_of_document::text );
    end if;

    -- cofk_union_manifestation 8. number_of_pages_of_text
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'number_of_pages_of_text',
        new.number_of_pages_of_text::text,
        old.number_of_pages_of_text::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'number_of_pages_of_text',
        new.number_of_pages_of_text::text );
    end if;

    -- cofk_union_manifestation 9. seal
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'seal',
        new.seal::text,
        old.seal::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'seal',
        new.seal::text );
    end if;

    -- cofk_union_manifestation 10. postage_marks
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'postage_marks',
        new.postage_marks::text,
        old.postage_marks::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'postage_marks',
        new.postage_marks::text );
    end if;

    -- cofk_union_manifestation 11. endorsements
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'endorsements',
        new.endorsements::text,
        old.endorsements::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'endorsements',
        new.endorsements::text );
    end if;

    -- cofk_union_manifestation 12. non_letter_enclosures
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'non_letter_enclosures',
        new.non_letter_enclosures::text,
        old.non_letter_enclosures::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'non_letter_enclosures',
        new.non_letter_enclosures::text );
    end if;

    -- cofk_union_manifestation 13. manifestation_creation_calendar
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_calendar',
        new.manifestation_creation_calendar::text,
        old.manifestation_creation_calendar::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_calendar',
        new.manifestation_creation_calendar::text );
    end if;

    -- cofk_union_manifestation 14. manifestation_creation_date
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_date',
        new.manifestation_creation_date::text,
        old.manifestation_creation_date::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_date',
        new.manifestation_creation_date::text );
    end if;

    -- cofk_union_manifestation 15. manifestation_creation_date_gregorian
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_date_gregorian',
        new.manifestation_creation_date_gregorian::text,
        old.manifestation_creation_date_gregorian::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_date_gregorian',
        new.manifestation_creation_date_gregorian::text );
    end if;

    -- cofk_union_manifestation 16. manifestation_creation_date_year
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_date_year',
        new.manifestation_creation_date_year::text,
        old.manifestation_creation_date_year::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_date_year',
        new.manifestation_creation_date_year::text );
    end if;

    -- cofk_union_manifestation 17. manifestation_creation_date_month
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_date_month',
        new.manifestation_creation_date_month::text,
        old.manifestation_creation_date_month::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_date_month',
        new.manifestation_creation_date_month::text );
    end if;

    -- cofk_union_manifestation 18. manifestation_creation_date_day
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_date_day',
        new.manifestation_creation_date_day::text,
        old.manifestation_creation_date_day::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_date_day',
        new.manifestation_creation_date_day::text );
    end if;

    -- cofk_union_manifestation 19. manifestation_creation_date_inferred
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_date_inferred',
        new.manifestation_creation_date_inferred::text,
        old.manifestation_creation_date_inferred::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_date_inferred',
        new.manifestation_creation_date_inferred::text );
    end if;

    -- cofk_union_manifestation 20. manifestation_creation_date_uncertain
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_date_uncertain',
        new.manifestation_creation_date_uncertain::text,
        old.manifestation_creation_date_uncertain::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_date_uncertain',
        new.manifestation_creation_date_uncertain::text );
    end if;

    -- cofk_union_manifestation 21. manifestation_creation_date_approx
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_date_approx',
        new.manifestation_creation_date_approx::text,
        old.manifestation_creation_date_approx::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_creation_date_approx',
        new.manifestation_creation_date_approx::text );
    end if;

    -- cofk_union_manifestation 22. manifestation_is_translation
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_is_translation',
        new.manifestation_is_translation::text,
        old.manifestation_is_translation::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_is_translation',
        new.manifestation_is_translation::text );
    end if;

    -- cofk_union_manifestation 23. language_of_manifestation
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'language_of_manifestation',
        new.language_of_manifestation::text,
        old.language_of_manifestation::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'language_of_manifestation',
        new.language_of_manifestation::text );
    end if;

    -- cofk_union_manifestation 24. address
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'address',
        new.address::text,
        old.address::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'address',
        new.address::text );
    end if;

    -- cofk_union_manifestation 25. manifestation_incipit
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_incipit',
        new.manifestation_incipit::text,
        old.manifestation_incipit::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_incipit',
        new.manifestation_incipit::text );
    end if;

    -- cofk_union_manifestation 26. manifestation_excipit
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_excipit',
        new.manifestation_excipit::text,
        old.manifestation_excipit::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_excipit',
        new.manifestation_excipit::text );
    end if;

    -- cofk_union_manifestation 27. manifestation_ps
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_ps',
        new.manifestation_ps::text,
        old.manifestation_ps::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_manifestation',
        new.manifestation_id,
        null,
        coalesce( new.id_number_or_shelfmark, '' ) || coalesce( new.printed_edition_details, '' ),
        'manifestation_ps',
        new.manifestation_ps::text );
    end if;

  end if; -- End of cofk_union_manifestation

-------------------

  if TG_RELNAME = 'cofk_union_person' then

    -- cofk_union_person 1. person_id
    if TG_OP = 'DELETE' then
      perform dbf_cofk_union_audit_literal_delete( 'cofk_union_person',
        old.person_id,
        old.iperson_id,
        old.foaf_name,
        'person_id',
        old.person_id::text );
    end if;

    -- cofk_union_person 2. foaf_name
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'foaf_name',
        new.foaf_name::text,
        old.foaf_name::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'foaf_name',
        new.foaf_name::text );
    end if;

    -- cofk_union_person 3. skos_altlabel
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'skos_altlabel',
        new.skos_altlabel::text,
        old.skos_altlabel::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'skos_altlabel',
        new.skos_altlabel::text );
    end if;

    -- cofk_union_person 4. skos_hiddenlabel
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'skos_hiddenlabel',
        new.skos_hiddenlabel::text,
        old.skos_hiddenlabel::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'skos_hiddenlabel',
        new.skos_hiddenlabel::text );
    end if;

    -- cofk_union_person 5. person_aliases
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'person_aliases',
        new.person_aliases::text,
        old.person_aliases::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'person_aliases',
        new.person_aliases::text );
    end if;

    -- cofk_union_person 6. date_of_birth_year
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth_year',
        new.date_of_birth_year::text,
        old.date_of_birth_year::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth_year',
        new.date_of_birth_year::text );
    end if;

    -- cofk_union_person 7. date_of_birth_month
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth_month',
        new.date_of_birth_month::text,
        old.date_of_birth_month::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth_month',
        new.date_of_birth_month::text );
    end if;

    -- cofk_union_person 8. date_of_birth_day
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth_day',
        new.date_of_birth_day::text,
        old.date_of_birth_day::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth_day',
        new.date_of_birth_day::text );
    end if;

    -- cofk_union_person 6x. date_of_birth2_year
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth2_year',
        new.date_of_birth2_year::text,
        old.date_of_birth2_year::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth2_year',
        new.date_of_birth2_year::text );
    end if;

    -- cofk_union_person 7x. date_of_birth2_month
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth2_month',
        new.date_of_birth2_month::text,
        old.date_of_birth2_month::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth2_month',
        new.date_of_birth2_month::text );
    end if;

    -- cofk_union_person 8x. date_of_birth2_day
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth2_day',
        new.date_of_birth2_day::text,
        old.date_of_birth2_day::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth2_day',
        new.date_of_birth2_day::text );
    end if;

    -- cofk_union_person 8xx. date_of_birth_calendar
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth_calendar',
        new.date_of_birth_calendar::text,
        old.date_of_birth_calendar::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth_calendar',
        new.date_of_birth_calendar::text );
    end if;

    -- cofk_union_person 8xxx. date_of_birth_is_range
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth_is_range',
        new.date_of_birth_is_range::text,
        old.date_of_birth_is_range::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth_is_range',
        new.date_of_birth_is_range::text );
    end if;

    -- cofk_union_person 9. date_of_birth
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth',
        new.date_of_birth::text,
        old.date_of_birth::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth',
        new.date_of_birth::text );
    end if;

    -- cofk_union_person 10. date_of_birth_inferred
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth_inferred',
        new.date_of_birth_inferred::text,
        old.date_of_birth_inferred::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth_inferred',
        new.date_of_birth_inferred::text );
    end if;

    -- cofk_union_person 11. date_of_birth_uncertain
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth_uncertain',
        new.date_of_birth_uncertain::text,
        old.date_of_birth_uncertain::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth_uncertain',
        new.date_of_birth_uncertain::text );
    end if;

    -- cofk_union_person 12. date_of_birth_approx
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth_approx',
        new.date_of_birth_approx::text,
        old.date_of_birth_approx::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_birth_approx',
        new.date_of_birth_approx::text );
    end if;

    -- cofk_union_person 13. date_of_death_year
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death_year',
        new.date_of_death_year::text,
        old.date_of_death_year::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death_year',
        new.date_of_death_year::text );
    end if;

    -- cofk_union_person 14. date_of_death_month
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death_month',
        new.date_of_death_month::text,
        old.date_of_death_month::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death_month',
        new.date_of_death_month::text );
    end if;

    -- cofk_union_person 15. date_of_death_day
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death_day',
        new.date_of_death_day::text,
        old.date_of_death_day::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death_day',
        new.date_of_death_day::text );
    end if;

    -- cofk_union_person 13x. date_of_death2_year
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death2_year',
        new.date_of_death2_year::text,
        old.date_of_death2_year::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death2_year',
        new.date_of_death2_year::text );
    end if;

    -- cofk_union_person 14x. date_of_death2_month
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death2_month',
        new.date_of_death2_month::text,
        old.date_of_death2_month::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death2_month',
        new.date_of_death2_month::text );
    end if;

    -- cofk_union_person 15x. date_of_death2_day
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death2_day',
        new.date_of_death2_day::text,
        old.date_of_death2_day::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death2_day',
        new.date_of_death2_day::text );
    end if;

    -- cofk_union_person 15xx. date_of_death_calendar
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death_calendar',
        new.date_of_death_calendar::text,
        old.date_of_death_calendar::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death_calendar',
        new.date_of_death_calendar::text );
    end if;

    -- cofk_union_person 15xxx. date_of_death_is_range
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death_is_range',
        new.date_of_death_is_range::text,
        old.date_of_death_is_range::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death_is_range',
        new.date_of_death_is_range::text );
    end if;


    -- cofk_union_person 16. date_of_death
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death',
        new.date_of_death::text,
        old.date_of_death::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death',
        new.date_of_death::text );
    end if;

    -- cofk_union_person 17. date_of_death_inferred
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death_inferred',
        new.date_of_death_inferred::text,
        old.date_of_death_inferred::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death_inferred',
        new.date_of_death_inferred::text );
    end if;

    -- cofk_union_person 18. date_of_death_uncertain
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death_uncertain',
        new.date_of_death_uncertain::text,
        old.date_of_death_uncertain::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death_uncertain',
        new.date_of_death_uncertain::text );
    end if;

    -- cofk_union_person 19. date_of_death_approx
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death_approx',
        new.date_of_death_approx::text,
        old.date_of_death_approx::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'date_of_death_approx',
        new.date_of_death_approx::text );
    end if;

    -- cofk_union_person 20. iperson_id
    if TG_OP = 'DELETE' then
      perform dbf_cofk_union_audit_literal_delete( 'cofk_union_person',
        old.person_id,
        old.iperson_id,
        old.foaf_name,
        'iperson_id',
        old.iperson_id::text );
    end if;

    -- cofk_union_person 21. editors_notes
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,  -- decode
        'editors_notes',
        new.editors_notes::text,
        old.editors_notes::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,  -- decode
        'editors_notes',
        new.editors_notes::text );
    end if;

    -- cofk_union_person 22. further_reading
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,  -- decode
        'further_reading',
        new.further_reading::text,
        old.further_reading::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,  -- decode
        'further_reading',
        new.further_reading::text );
    end if;

    -- cofk_union_person 23. flourished_year
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'flourished_year',
        new.flourished_year::text,
        old.flourished_year::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'flourished_year',
        new.flourished_year::text );
    end if;

    -- cofk_union_person 24. flourished_month
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'flourished_month',
        new.flourished_month::text,
        old.flourished_month::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'flourished_month',
        new.flourished_month::text );
    end if;

    -- cofk_union_person 25. flourished_day
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'flourished_day',
        new.flourished_day::text,
        old.flourished_day::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'flourished_day',
        new.flourished_day::text );
    end if;

    -- cofk_union_person 26. flourished2_year
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'flourished2_year',
        new.flourished2_year::text,
        old.flourished2_year::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'flourished2_year',
        new.flourished2_year::text );
    end if;

    -- cofk_union_person 27. flourished2_month
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'flourished2_month',
        new.flourished2_month::text,
        old.flourished2_month::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'flourished2_month',
        new.flourished2_month::text );
    end if;

    -- cofk_union_person 28. flourished2_day
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'flourished2_day',
        new.flourished2_day::text,
        old.flourished2_day::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'flourished2_day',
        new.flourished2_day::text );
    end if;

    -- cofk_union_person 29. flourished_calendar
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'flourished_calendar',
        new.flourished_calendar::text,
        old.flourished_calendar::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'flourished_calendar',
        new.flourished_calendar::text );
    end if;

    -- cofk_union_person 30. flourished_is_range
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'flourished_is_range',
        new.flourished_is_range::text,
        old.flourished_is_range::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'flourished_is_range',
        new.flourished_is_range::text );
    end if;

    -- cofk_union_person: organisation type
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'organisation_type',
        coalesce( ( select org_type_desc from cofk_union_org_type where org_type_id = new.organisation_type ),
                  '' ),
        coalesce( ( select org_type_desc from cofk_union_org_type where org_type_id = old.organisation_type ),
                  '' ) );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_person',
        new.person_id,
        new.iperson_id,
        new.foaf_name,
        'organisation_type',
        coalesce( ( select org_type_desc from cofk_union_org_type where org_type_id = new.organisation_type),
                  '' ) );
    end if;


  end if; -- End of cofk_union_person

-------------------

  if TG_RELNAME = 'cofk_union_publication' then

    -- cofk_union_publication 1. publication_id
    if TG_OP = 'DELETE' then
      perform dbf_cofk_union_audit_literal_delete( 'cofk_union_publication',
        old.publication_id::text,
        old.publication_id,
        old.publication_details,
        'publication_id',
        old.publication_id::text );
    end if;

    -- cofk_union_publication 2. publication_details
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_publication',
        new.publication_id::text,
        new.publication_id,
        new.publication_details,
        'publication_details',
        new.publication_details::text,
        old.publication_details::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_publication',
        new.publication_id::text,
        new.publication_id,
        new.publication_details,
        'publication_details',
        new.publication_details::text );
    end if;

    -- cofk_union_publication 2. abbreviation
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_publication',
        new.publication_id::text,
        new.publication_id,
        new.publication_details,
        'abbrev',
        new.abbrev::text,
        old.abbrev::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_publication',
        new.publication_id::text,
        new.publication_id,
        new.publication_details,
        'abbrev',
        new.abbrev::text );
    end if;

  end if; -- End of cofk_union_publication

-------------------

  if TG_RELNAME = 'cofk_union_relationship' then

    -- cofk_union_relationship 1. relationship_id
    if TG_OP = 'UPDATE' then
      ------------------------------------
      -- Change of ID value on either side
      ------------------------------------
      if new.left_id_value != old.left_id_value or new.right_id_value != old.right_id_value then
        perform dbf_cofk_union_audit_relationship_update(
          new.left_table_name,
          new.left_id_value,
          (select dbf_cofk_union_decode( new.left_table_name, new.left_id_value )),
          old.left_id_value,
          (select dbf_cofk_union_decode( old.left_table_name, old.left_id_value )),
          new.relationship_type,
          (select desc_left_to_right from cofk_union_relationship_type
          where relationship_code = new.relationship_type),
          (select desc_right_to_left from cofk_union_relationship_type
          where relationship_code = new.relationship_type),
          new.right_table_name,
          new.right_id_value,
          (select dbf_cofk_union_decode( new.right_table_name, new.right_id_value )),
          old.right_id_value,
          (select dbf_cofk_union_decode( old.right_table_name, old.right_id_value ))
        );
      end if;

      if new.right_id_value != old.right_id_value then
        perform dbf_cofk_union_audit_literal_update( new.left_table_name,
          new.left_id_value,
          new.relationship_id,  -- integer ID here holds relationship ID
          (select dbf_cofk_union_decode( new.left_table_name, new.left_id_value )),
          (select 'Relationship: ' || desc_left_to_right from cofk_union_relationship_type
           where relationship_code = new.relationship_type),
          (select dbf_cofk_union_decode( new.right_table_name, new.right_id_value )),
          (select dbf_cofk_union_decode( old.right_table_name, old.right_id_value ))
        );
        perform dbf_cofk_union_audit_literal_insert( new.right_table_name,
          new.right_id_value,
          new.relationship_id,  -- integer ID here holds relationship ID
          (select dbf_cofk_union_decode( new.right_table_name, new.right_id_value )),
          (select 'Relationship: ' || desc_right_to_left from cofk_union_relationship_type
           where relationship_code = new.relationship_type),
          (select dbf_cofk_union_decode( new.left_table_name, new.left_id_value ))
        );
        perform dbf_cofk_union_audit_literal_delete( old.right_table_name,
          old.right_id_value,
          old.relationship_id,  -- integer ID here holds relationship ID
          (select dbf_cofk_union_decode( old.right_table_name, old.right_id_value )),
          (select 'Relationship: ' || desc_right_to_left from cofk_union_relationship_type
           where relationship_code = old.relationship_type),
          (select dbf_cofk_union_decode( old.left_table_name, old.left_id_value ))
        );
      end if;

      if new.left_id_value != old.left_id_value then
        perform dbf_cofk_union_audit_literal_update( new.right_table_name,
          new.right_id_value,
          new.relationship_id,  -- integer ID here holds relationship ID
          (select dbf_cofk_union_decode( new.right_table_name, new.right_id_value )),
          (select 'Relationship: ' || desc_right_to_left from cofk_union_relationship_type
           where relationship_code = new.relationship_type),
          (select dbf_cofk_union_decode( new.left_table_name, new.left_id_value )),
          (select dbf_cofk_union_decode( old.left_table_name, old.left_id_value ))
        );
        perform dbf_cofk_union_audit_literal_insert( new.left_table_name,
          new.left_id_value,
          new.relationship_id,  -- integer ID here holds relationship ID
          (select dbf_cofk_union_decode( new.left_table_name, new.left_id_value )),
          (select 'Relationship: ' || desc_left_to_right from cofk_union_relationship_type
           where relationship_code = new.relationship_type),
          (select dbf_cofk_union_decode( new.right_table_name, new.right_id_value ))
        );
        perform dbf_cofk_union_audit_literal_delete( old.left_table_name,
          old.left_id_value,
          old.relationship_id,  -- integer ID here holds relationship ID
          (select dbf_cofk_union_decode( old.left_table_name, old.left_id_value )),
          (select 'Relationship: ' || desc_left_to_right from cofk_union_relationship_type
           where relationship_code = old.relationship_type),
          (select dbf_cofk_union_decode( old.right_table_name, old.right_id_value ))
        );
      end if;

      ------------------------------------
      -- Change of relationship start date
      ------------------------------------
      if coalesce( new.relationship_valid_from, '9999-12-31'::date )
      != coalesce( old.relationship_valid_from, '9999-12-31'::date ) then

        perform dbf_cofk_union_audit_literal_update(

          'cofk_union_relationship',   -- table_name

          new.left_id_value || ' ' || new.right_id_value, -- key_value_text

          new.relationship_id,  -- key_value_integer

          (select dbf_cofk_union_decode( new.left_table_name, new.left_id_value ))
            || ' '
            || (select desc_left_to_right from cofk_union_relationship_type
                where relationship_code = new.relationship_type)
            || ' '
            || (select dbf_cofk_union_decode( new.right_table_name, new.right_id_value )), -- key_decode

          'relationship_valid_from',   -- column_name
          new.relationship_valid_from::date::text, -- new_column_value
          old.relationship_valid_from::date::text  -- old_column_value
        );
      end if;

      ------------------------------------
      -- Change of relationship end date
      ------------------------------------
      if coalesce( new.relationship_valid_till, '9999-12-31'::date )
      != coalesce( old.relationship_valid_till, '9999-12-31'::date ) then

        perform dbf_cofk_union_audit_literal_update(

          'cofk_union_relationship',   -- table_name

          new.left_id_value || ' ' || new.right_id_value, -- key_value_text

          new.relationship_id,  -- key_value_integer

          (select dbf_cofk_union_decode( new.left_table_name, new.left_id_value ))
            || ' '
            || (select desc_left_to_right from cofk_union_relationship_type
                where relationship_code = new.relationship_type)
            || ' '
            || (select dbf_cofk_union_decode( new.right_table_name, new.right_id_value )), -- key_decode

          'relationship_valid_till',    -- column_name
          new.relationship_valid_till::date::text, -- new_column_value
          old.relationship_valid_till::date::text  -- old_column_value
        );
      end if;
    end if;  -- end of 'relationship update' section

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_relationship_insert(
        new.left_table_name,
        new.left_id_value,
        (select dbf_cofk_union_decode( new.left_table_name, new.left_id_value )),
        new.relationship_type,
        (select desc_left_to_right from cofk_union_relationship_type
        where relationship_code = new.relationship_type),
        (select desc_right_to_left from cofk_union_relationship_type
        where relationship_code = new.relationship_type),
        new.right_table_name,
        new.right_id_value,
        (select dbf_cofk_union_decode( new.right_table_name, new.right_id_value ))
      );

      perform dbf_cofk_union_audit_literal_insert( new.left_table_name,
        new.left_id_value,
        new.relationship_id,  -- integer ID here holds relationship ID
        (select dbf_cofk_union_decode( new.left_table_name, new.left_id_value )),
        (select 'Relationship: ' || desc_left_to_right from cofk_union_relationship_type
         where relationship_code = new.relationship_type),
        (select dbf_cofk_union_decode( new.right_table_name, new.right_id_value ))
      );
      perform dbf_cofk_union_audit_literal_insert( new.right_table_name,
        new.right_id_value,
        new.relationship_id,  -- integer ID here holds relationship ID
        (select dbf_cofk_union_decode( new.right_table_name, new.right_id_value )),
        (select 'Relationship: ' || desc_right_to_left from cofk_union_relationship_type
         where relationship_code = new.relationship_type),
        (select dbf_cofk_union_decode( new.left_table_name, new.left_id_value ))
      );

      ------------------------------
      -- New relationship start date
      ------------------------------
      perform dbf_cofk_union_audit_literal_insert(

        'cofk_union_relationship',   -- table_name

        new.left_id_value || ' ' || new.right_id_value, -- key_value_text

        new.relationship_id,  -- key_value_integer

        (select dbf_cofk_union_decode( new.left_table_name, new.left_id_value ))
          || ' '
          || (select desc_left_to_right from cofk_union_relationship_type
              where relationship_code = new.relationship_type)
          || ' '
          || (select dbf_cofk_union_decode( new.right_table_name, new.right_id_value )), -- key_decode

        'relationship_valid_from',    -- column_name
        new.relationship_valid_from::date::text   -- new_column_value
      );

      ------------------------------
      -- New relationship end date
      ------------------------------
      perform dbf_cofk_union_audit_literal_insert(

        'cofk_union_relationship',   -- table_name

        new.left_id_value || ' ' || new.right_id_value, -- key_value_text

        new.relationship_id,  -- key_value_integer

        (select dbf_cofk_union_decode( new.left_table_name, new.left_id_value ))
          || ' '
          || (select desc_left_to_right from cofk_union_relationship_type
              where relationship_code = new.relationship_type)
          || ' '
          || (select dbf_cofk_union_decode( new.right_table_name, new.right_id_value )), -- key_decode

        'relationship_valid_till',    -- column_name
        new.relationship_valid_till::date::text   -- new_column_value
      );
    end if;

    if TG_OP = 'DELETE' then
      perform dbf_cofk_union_audit_relationship_delete(
        old.left_table_name,
        old.left_id_value,
        (select dbf_cofk_union_decode( old.left_table_name, old.left_id_value )),
        old.relationship_type,
        (select desc_left_to_right from cofk_union_relationship_type
        where relationship_code = old.relationship_type),
        (select desc_right_to_left from cofk_union_relationship_type
        where relationship_code = old.relationship_type),
        old.right_table_name,
        old.right_id_value,
        (select dbf_cofk_union_decode( old.right_table_name, old.right_id_value ))
      );

      perform dbf_cofk_union_audit_literal_delete( old.left_table_name,
        old.left_id_value,
        old.relationship_id,  -- integer ID here holds relationship ID
        (select dbf_cofk_union_decode( old.left_table_name, old.left_id_value )),
        (select 'Relationship: ' || desc_left_to_right from cofk_union_relationship_type
         where relationship_code = old.relationship_type),
        (select dbf_cofk_union_decode( old.right_table_name, old.right_id_value ))
      );
      perform dbf_cofk_union_audit_literal_delete( old.right_table_name,
        old.right_id_value,
        old.relationship_id,  -- integer ID here holds relationship ID
        (select dbf_cofk_union_decode( old.right_table_name, old.right_id_value )),
        (select 'Relationship: ' || desc_right_to_left from cofk_union_relationship_type
         where relationship_code = old.relationship_type),
        (select dbf_cofk_union_decode( old.left_table_name, old.left_id_value ))
      );
    end if;

    -- cofk_union_relationship 2. left_table_name
    -- cofk_union_relationship 3. left_id_value
    -- cofk_union_relationship 4. relationship_type
    -- cofk_union_relationship 5. right_table_name
    -- cofk_union_relationship 6. right_id_value
    -- cofk_union_relationship 7. relationship_valid_from
    -- cofk_union_relationship 8. relationship_valid_till
  end if; -- End of cofk_union_relationship

-------------------

  if TG_RELNAME = 'cofk_union_relationship_type' then

    -- cofk_union_relationship_type 1. relationship_code
    if TG_OP = 'DELETE' then
      perform dbf_cofk_union_audit_literal_delete( 'cofk_union_relationship_type',
        old.relationship_code,
        null,
        old.desc_left_to_right,
        'relationship_code',
        old.relationship_code::text );
    end if;

    -- cofk_union_relationship_type 2. desc_left_to_right
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_relationship_type',
        new.relationship_code,
        null,
        new.desc_left_to_right,
        'desc_left_to_right',
        new.desc_left_to_right::text,
        old.desc_left_to_right::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_relationship_type',
        new.relationship_code,
        null,
        new.desc_left_to_right,
        'desc_left_to_right',
        new.desc_left_to_right::text );
    end if;

    -- cofk_union_relationship_type 3. desc_right_to_left
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_relationship_type',
        new.relationship_code,
        null,
        new.desc_left_to_right,
        'desc_right_to_left',
        new.desc_right_to_left::text,
        old.desc_right_to_left::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_relationship_type',
        new.relationship_code,
        null,
        new.desc_left_to_right,
        'desc_right_to_left',
        new.desc_right_to_left::text );
    end if;

  end if; -- End of cofk_union_relationship_type

-------------------

  if TG_RELNAME = 'cofk_union_resource' then

    -- cofk_union_resource 1. resource_id
    if TG_OP = 'DELETE' then
      perform dbf_cofk_union_audit_literal_delete( 'cofk_union_resource',
        old.resource_id::text,
        old.resource_id,
        old.resource_name,
        'resource_id',
        old.resource_id::text );
    end if;

    -- cofk_union_resource 2. resource_name
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_resource',
        new.resource_id::text,
        new.resource_id,
        new.resource_name,
        'resource_name',
        new.resource_name::text,
        old.resource_name::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_resource',
        new.resource_id::text,
        new.resource_id,
        new.resource_name,
        'resource_name',
        new.resource_name::text );
    end if;

    -- cofk_union_resource 3. resource_details
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_resource',
        new.resource_id::text,
        new.resource_id,
        new.resource_name,
        'resource_details',
        new.resource_details::text,
        old.resource_details::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_resource',
        new.resource_id::text,
        new.resource_id,
        new.resource_name,
        'resource_details',
        new.resource_details::text );
    end if;

    -- cofk_union_resource 4. resource_url
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_resource',
        new.resource_id::text,
        new.resource_id,
        new.resource_name,
        'resource_url',
        new.resource_url::text,
        old.resource_url::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_resource',
        new.resource_id::text,
        new.resource_id,
        new.resource_name,
        'resource_url',
        new.resource_url::text );
    end if;

  end if; -- End of cofk_union_resource

-------------------

  if TG_RELNAME = 'cofk_union_work' then

    -- cofk_union_work 1. work_id
    if TG_OP = 'DELETE' then
      perform dbf_cofk_union_audit_literal_delete( 'cofk_union_work',
        old.work_id,
        old.iwork_id,
        old.description,
        'work_id',
        old.work_id::text );
    end if;

    -- cofk_union_work 2. description
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'description',
        new.description::text,
        old.description::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'description',
        new.description::text );
    end if;

    -- cofk_union_work 3. date_of_work_as_marked
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_as_marked',
        new.date_of_work_as_marked::text,
        old.date_of_work_as_marked::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_as_marked',
        new.date_of_work_as_marked::text );
    end if;

    -- cofk_union_work 4. original_calendar
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'original_calendar',
        new.original_calendar::text,
        old.original_calendar::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'original_calendar',
        new.original_calendar::text );
    end if;

    -- cofk_union_work 5. date_of_work_std
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_std',
        new.date_of_work_std::text,
        old.date_of_work_std::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_std',
        new.date_of_work_std::text );
    end if;

    -- cofk_union_work 6. date_of_work_std_gregorian
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_std_gregorian',
        new.date_of_work_std_gregorian::text,
        old.date_of_work_std_gregorian::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_std_gregorian',
        new.date_of_work_std_gregorian::text );
    end if;

    -- cofk_union_work 7. date_of_work_std_year
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_std_year',
        new.date_of_work_std_year::text,
        old.date_of_work_std_year::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_std_year',
        new.date_of_work_std_year::text );
    end if;

    -- cofk_union_work 8. date_of_work_std_month
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_std_month',
        new.date_of_work_std_month::text,
        old.date_of_work_std_month::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_std_month',
        new.date_of_work_std_month::text );
    end if;

    -- cofk_union_work 9. date_of_work_std_day
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_std_day',
        new.date_of_work_std_day::text,
        old.date_of_work_std_day::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_std_day',
        new.date_of_work_std_day::text );
    end if;

    -- cofk_union_work 10. date_of_work2_std_year
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work2_std_year',
        new.date_of_work2_std_year::text,
        old.date_of_work2_std_year::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work2_std_year',
        new.date_of_work2_std_year::text );
    end if;

    -- cofk_union_work 11. date_of_work2_std_month
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work2_std_month',
        new.date_of_work2_std_month::text,
        old.date_of_work2_std_month::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work2_std_month',
        new.date_of_work2_std_month::text );
    end if;

    -- cofk_union_work 12. date_of_work2_std_day
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work2_std_day',
        new.date_of_work2_std_day::text,
        old.date_of_work2_std_day::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work2_std_day',
        new.date_of_work2_std_day::text );
    end if;

    -- cofk_union_work 13. date_of_work_std_is_range
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_std_is_range',
        new.date_of_work_std_is_range::text,
        old.date_of_work_std_is_range::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_std_is_range',
        new.date_of_work_std_is_range::text );
    end if;

    -- cofk_union_work 14. date_of_work_inferred
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_inferred',
        new.date_of_work_inferred::text,
        old.date_of_work_inferred::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_inferred',
        new.date_of_work_inferred::text );
    end if;

    -- cofk_union_work 15. date_of_work_uncertain
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_uncertain',
        new.date_of_work_uncertain::text,
        old.date_of_work_uncertain::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_uncertain',
        new.date_of_work_uncertain::text );
    end if;

    -- cofk_union_work 16. date_of_work_approx
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_approx',
        new.date_of_work_approx::text,
        old.date_of_work_approx::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'date_of_work_approx',
        new.date_of_work_approx::text );
    end if;

    -- cofk_union_work 17. authors_as_marked
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'authors_as_marked',
        new.authors_as_marked::text,
        old.authors_as_marked::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'authors_as_marked',
        new.authors_as_marked::text );
    end if;

    -- cofk_union_work 18. addressees_as_marked
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'addressees_as_marked',
        new.addressees_as_marked::text,
        old.addressees_as_marked::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'addressees_as_marked',
        new.addressees_as_marked::text );
    end if;

    -- cofk_union_work 19. authors_inferred
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'authors_inferred',
        new.authors_inferred::text,
        old.authors_inferred::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'authors_inferred',
        new.authors_inferred::text );
    end if;

    -- cofk_union_work 20. authors_uncertain
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'authors_uncertain',
        new.authors_uncertain::text,
        old.authors_uncertain::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'authors_uncertain',
        new.authors_uncertain::text );
    end if;

    -- cofk_union_work 21. addressees_inferred
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'addressees_inferred',
        new.addressees_inferred::text,
        old.addressees_inferred::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'addressees_inferred',
        new.addressees_inferred::text );
    end if;

    -- cofk_union_work 22. addressees_uncertain
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'addressees_uncertain',
        new.addressees_uncertain::text,
        old.addressees_uncertain::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'addressees_uncertain',
        new.addressees_uncertain::text );
    end if;

    -- cofk_union_work 23. destination_as_marked
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'destination_as_marked',
        new.destination_as_marked::text,
        old.destination_as_marked::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'destination_as_marked',
        new.destination_as_marked::text );
    end if;

    -- cofk_union_work 24. origin_as_marked
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'origin_as_marked',
        new.origin_as_marked::text,
        old.origin_as_marked::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'origin_as_marked',
        new.origin_as_marked::text );
    end if;

    -- cofk_union_work 25. destination_inferred
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'destination_inferred',
        new.destination_inferred::text,
        old.destination_inferred::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'destination_inferred',
        new.destination_inferred::text );
    end if;

    -- cofk_union_work 26. destination_uncertain
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'destination_uncertain',
        new.destination_uncertain::text,
        old.destination_uncertain::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'destination_uncertain',
        new.destination_uncertain::text );
    end if;

    -- cofk_union_work 27. origin_inferred
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'origin_inferred',
        new.origin_inferred::text,
        old.origin_inferred::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'origin_inferred',
        new.origin_inferred::text );
    end if;

    -- cofk_union_work 28. origin_uncertain
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'origin_uncertain',
        new.origin_uncertain::text,
        old.origin_uncertain::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'origin_uncertain',
        new.origin_uncertain::text );
    end if;

    -- cofk_union_work 29. abstract
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'abstract',
        new.abstract::text,
        old.abstract::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'abstract',
        new.abstract::text );
    end if;

    -- cofk_union_work 30. keywords
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'keywords',
        new.keywords::text,
        old.keywords::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'keywords',
        new.keywords::text );
    end if;

    -- cofk_union_work 32. work_is_translation
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'work_is_translation',
        new.work_is_translation::text,
        old.work_is_translation::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'work_is_translation',
        new.work_is_translation::text );
    end if;

    -- cofk_union_work 33. incipit
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'incipit',
        new.incipit::text,
        old.incipit::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'incipit',
        new.incipit::text );
    end if;

    -- cofk_union_work 34. explicit
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'explicit',
        new.explicit::text,
        old.explicit::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'explicit',
        new.explicit::text );
    end if;

    -- cofk_union_work 35. ps
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'ps',
        new.ps::text,
        old.ps::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'ps',
        new.ps::text );
    end if;

    -- cofk_union_work 36. accession_code
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'accession_code',
        new.accession_code::text,
        old.accession_code::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'accession_code',
        new.accession_code::text );
    end if;

    -- cofk_union_work 37. work_to_be_deleted
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'work_to_be_deleted',
        new.work_to_be_deleted::text,
        old.work_to_be_deleted::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'work_to_be_deleted',
        new.work_to_be_deleted::text );
    end if;


    if TG_OP = 'DELETE' then
      perform dbf_cofk_union_audit_literal_delete( 'cofk_union_work',
        old.work_id,
        old.iwork_id,
        old.description,
        'iwork_id',
        old.iwork_id::text );
    end if;

    -- cofk_union_work 39. editors_notes
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'editors_notes',
        new.editors_notes::text,
        old.editors_notes::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'editors_notes',
        new.editors_notes::text );
    end if;

    -- cofk_union_work 40. edit_status
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'edit_status',
        new.edit_status::text,
        old.edit_status::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'edit_status',
        new.edit_status::text );
    end if;

    -- cofk_union_work 41. relevant_to_cofk
    if TG_OP = 'UPDATE' then
      perform dbf_cofk_union_audit_literal_update( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'relevant_to_cofk',
        new.relevant_to_cofk::text,
        old.relevant_to_cofk::text );
    end if;

    if TG_OP = 'INSERT' then
      perform dbf_cofk_union_audit_literal_insert( 'cofk_union_work',
        new.work_id,
        new.iwork_id,
        new.description,
        'relevant_to_cofk',
        new.relevant_to_cofk::text );
    end if;

  end if; -- End of cofk_union_work

-------------------

  if TG_RELNAME = 'INSERT' or TG_RELNAME = 'UPDATE' then
    return new;
  else
    return old;
  end if;
end;
$$;

alter function dbf_cofk_union_audit_any() owner to postgres;

-- grant execute on function dbf_cofk_union_audit_any() to editor_role_cofk;

