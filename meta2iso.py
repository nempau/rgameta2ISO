from gis_metadata.iso_metadata_parser import IsoParser
from pygeometa.core import render_template
import yaml
import glob
import os
from os.path import basename
import time 



class RGAIsoParser(IsoParser):

    def _init_data_map(self):
        super(RGAIsoParser, self)._init_data_map()

        # Basic property: text or list (with backup location referencing codeListValue attribute)

        lang_prop = 'metadata_language'
        self._data_map[lang_prop] = 'language/CharacterString'                    # Parse from here if present
        self._data_map['_' + lang_prop] = 'language/LanguageCode/@codeListValue'  # Otherwise, try from here
        
        fileident_prop='fileIdentifier'
        self._data_map[fileident_prop] = 'fileIdentifier/CharacterString'
        
        hierarchyLevel_prop='hierarchyLevel'
        self._data_map[hierarchyLevel_prop] = 'hierarchyLevel/MD_ScopeCode'                    # Parse from here if present
        self._data_map['_' + hierarchyLevel_prop] = 'hierarchyLevel/MD_ScopeCode/@codeListValue'  # Otherwise, try from here
        
        #10.1
        #Metadata point of conntact organisation
        meta_organization_name_prop= 'meta_organization_name'
        self._data_map[meta_organization_name_prop] = 'contact/CI_ResponsibleParty/organisationName/CharacterString'
        
        #10.1
        #Metadata point of conntact organisation_emailAddress
        meta_organisation_emailAddress_prop = 'meta_organisation_emailAddress'
        self._data_map[meta_organisation_emailAddress_prop] = 'contact/CI_ResponsibleParty/contactInfo/CI_Contact/address/CI_Address/electronicMailAddress/CharacterString'
        
        #10.2
        #Matadata date
        dateStamp_prop= 'dateStamp'
        self._data_map[dateStamp_prop] = 'dateStamp/Date'
        
        metadataStandardName_prop = 'metadataStandardName'
        self._data_map[metadataStandardName_prop] ='metadataStandardName/CharacterString'
        
        metadataStandardVersion_prop = 'metadataStandardVersion'
        self._data_map[metadataStandardVersion_prop] ='metadataStandardVersion/CharacterString'
        
        publish_date_prop='publish_date'
        self._data_map[publish_date_prop] ='identificationInfo/MD_DataIdentification/citation/CI_Citation/date/CI_Date/date/DateTime'
        
        dateTypeCode_prop='dateTypeCode'
        self._data_map[dateTypeCode_prop] ='identificationInfo/MD_DataIdentification/citation/CI_Citation/date/CI_Date/dateType/CI_DateTypeCode'
        
        RS_Identifier_prop='RS_Identifier'
        self._data_map[RS_Identifier_prop] = 'identificationInfo/MD_DataIdentification/citation/CI_Citation/identifier/RS_Identifier/code/CharacterString'
        
        RS_Identifier_codeSpace_prop='RS_Identifier_codeSpace'
        self._data_map[RS_Identifier_codeSpace_prop] = 'identificationInfo/MD_DataIdentification/citation/CI_Citation/identifier/RS_Identifier/codeSpace/CharacterString'
        
        #9.1.
        #Responsible party organisationName
        organisationName_prop='organisationName'
        self._data_map[organisationName_prop] = 'identificationInfo/MD_DataIdentification/pointOfContact/CI_ResponsibleParty/organisationName/CharacterString'
        
        #9.1.
        #Responsible party organisation_emailAddress_prop
        resp_organisation_emailAddress_prop='organisation_emailAddress'
        self._data_map[resp_organisation_emailAddress_prop] = 'identificationInfo/MD_DataIdentification/pointOfContact/CI_ResponsibleParty/contactInfo/CI_Contact/address/CI_Address/electronicMailAddress/CharacterString'
        
        #9.1.
        #Responsible party organisation role
        organisation_role_prop= 'organisation_role'
        self._data_map[organisation_role_prop] = 'identificationInfo/MD_DataIdentification/pointOfContact/CI_ResponsibleParty/role/CI_RoleCode'
        self._data_map['_' + organisation_role_prop] =         'identificationInfo/MD_DataIdentification/pointOfContact/CI_ResponsibleParty/role/CI_RoleCode/@codeListValue' # Otherwise, try from here
        
        #9.1.
        #Distribution Contact organisation - Duplirano
        dist_contact_org_prop = 'dist_contact_org'
        self._data_map[dist_contact_org_prop] = 'ExtensionBlock/Distribution/distributor/organisationName/CharacterString'
        
        #9.1.
        #Distribution Contact organisation_emailAddress_prop - Duplirano
        dist_email_prop = 'dist_email'
        self._data_map[dist_email_prop] = 'ExtensionBlock/Distribution/distributor/emailAddress/CharacterString'
        
        dist_format_prop = 'dist_format'
        self._data_map[dist_format_prop] = 'ExtensionBlock/Distribution/distributionFormat/CharacterString'
        
        descriptiveKeywords_prop='descriptiveKeywords'
        self._data_map[descriptiveKeywords_prop] = 'identificationInfo/MD_DataIdentification/descriptiveKeywords/MD_Keywords/keyword/CharacterString'
        
        useLimitation_prop = 'useLimitation'
        self._data_map[useLimitation_prop]= 'identificationInfo/MD_DataIdentification/resourceConstraints/MD_Constraints/useLimitation/CharacterString'
        
        accessConstraints_prop = 'accessConstraints'
        self._data_map[accessConstraints_prop] = 'identificationInfo/MD_DataIdentification/resourceConstraints/MD_LegalConstraints/accessConstraints/MD_RestrictionCode'
        
        otherConstraints_prop = 'otherConstraints'
        self._data_map[otherConstraints_prop] = 'identificationInfo/MD_DataIdentification/resourceConstraints/MD_LegalConstraints/otherConstraints/CharacterString'
        
        denominator_prop = 'denominator'
        self._data_map[denominator_prop] = 'identificationInfo/MD_DataIdentification/spatialResolution/MD_Resolution/equivalentScale/MD_RepresentativeFraction/denominator/Integer'
        
        distance_prop = 'distance'
        self._data_map[distance_prop] = 'identificationInfo/MD_DataIdentification/spatialResolution/MD_Resolution/distance/Distance'
        
        resourceLanguage_prop= 'resourceLanguage'
        self._data_map[resourceLanguage_prop]='identificationInfo/MD_DataIdentification/language/LanguageCode'
        
        inspireCategory_prop = 'inspireCategory'
        self._data_map[inspireCategory_prop] = 'identificationInfo/MD_DataIdentification/topicCategory/MD_TopicCategoryCode'
        
        westBoundLongitude_prop = 'westBoundLongitude'
        self._data_map[westBoundLongitude_prop]='identificationInfo/MD_DataIdentification/extent/EX_Extent/geographicElement/EX_GeographicBoundingBox/westBoundLongitude/Decimal'
        
        eastBoundLongitude_prop = 'eastBoundLongitude'
        self._data_map[eastBoundLongitude_prop]='identificationInfo/MD_DataIdentification/extent/EX_Extent/geographicElement/EX_GeographicBoundingBox/eastBoundLongitude/Decimal'
        
        southBoundLatitude_prop = 'southBoundLatitude'
        self._data_map[southBoundLatitude_prop]='identificationInfo/MD_DataIdentification/extent/EX_Extent/geographicElement/EX_GeographicBoundingBox/southBoundLatitude/Decimal'
        
        northBoundLatitude_prop = 'northBoundLatitude'
        self._data_map[northBoundLatitude_prop]='identificationInfo/MD_DataIdentification/extent/EX_Extent/geographicElement/EX_GeographicBoundingBox/northBoundLatitude/Decimal'
        
        #temporalElement
        t_extnt_beginPosition_prop= 't_extnt_beginPosition'
        self._data_map[t_extnt_beginPosition_prop]= 'identificationInfo/MD_DataIdentification/extent/EX_Extent/temporalElement/EX_TemporalExtent/extent/TimePeriod/beginPosition'
        
        t_extnt_endPosition_prop = 't_extnt_endPosition'
        self._data_map[t_extnt_endPosition_prop]= 'identificationInfo/MD_DataIdentification/extent/EX_Extent/temporalElement/EX_TemporalExtent/extent/TimePeriod/endPosition'
        
        linkage_prop = 'linkage'
        self._data_map[linkage_prop] = 'distributionInfo/MD_Distribution/transferOptions/MD_DigitalTransferOptions/onLine/CI_OnlineResource/linkage/URL'
        
        lineage_prop = 'lineage'
        self._data_map[lineage_prop] = 'dataQualityInfo/DQ_DataQuality/lineage/LI_Lineage/statement/CharacterString'

        # And finally, let the parent validation logic know about the two new custom properties

        self._metadata_props.add(lang_prop)
        self._metadata_props.add(fileident_prop)
        self._metadata_props.add(hierarchyLevel_prop)
        self._metadata_props.add(meta_organization_name_prop)
        self._metadata_props.add(meta_organisation_emailAddress_prop)
        self._metadata_props.add(dateStamp_prop)
        self._metadata_props.add(metadataStandardName_prop)
        self._metadata_props.add(metadataStandardVersion_prop)
        self._metadata_props.add(publish_date_prop)
        self._metadata_props.add(dateTypeCode_prop)
        self._metadata_props.add(RS_Identifier_prop)
        self._metadata_props.add(RS_Identifier_codeSpace_prop)
        self._metadata_props.add(organisationName_prop)
        self._metadata_props.add(resp_organisation_emailAddress_prop)
        self._metadata_props.add(organisation_role_prop)
        self._metadata_props.add(dist_contact_org_prop)
        self._metadata_props.add(dist_email_prop)
        self._metadata_props.add(dist_format_prop)
        self._metadata_props.add(descriptiveKeywords_prop)
        self._metadata_props.add(useLimitation_prop)
        self._metadata_props.add(accessConstraints_prop)
        self._metadata_props.add(otherConstraints_prop)
        self._metadata_props.add(denominator_prop)
        self._metadata_props.add(distance_prop)
        self._metadata_props.add(resourceLanguage_prop)
        self._metadata_props.add(inspireCategory_prop)
        self._metadata_props.add(westBoundLongitude_prop)
        self._metadata_props.add(eastBoundLongitude_prop)
        self._metadata_props.add(southBoundLatitude_prop)
        self._metadata_props.add(northBoundLatitude_prop)
        self._metadata_props.add(t_extnt_beginPosition_prop)
        self._metadata_props.add(t_extnt_endPosition_prop)
        self._metadata_props.add(linkage_prop)
        self._metadata_props.add(lineage_prop)
        
def makeyml(fxml_path, ymls_dts_dir):
    with open(fxml_path) as metadata:
      old_schema_file = RGAIsoParser(metadata)

    
      data = dict(mcf = dict(version = '1.0.0'
			   ),
		  metadata = dict(
		  identifier = old_schema_file.fileIdentifier,
		  language = old_schema_file.metadata_language,
		  hierarchylevel = old_schema_file.hierarchyLevel,
		  organization_name = old_schema_file.meta_organization_name,
		  organisation_emailAddress = old_schema_file.meta_organisation_emailAddress,
		  datestamp = old_schema_file.dateStamp,
		  title = old_schema_file.title,
		  # Datum kreiranja, izmene, publikacije i njegov tip
		  publish_date = old_schema_file.publish_date,
		  dateTypeCode = old_schema_file.dateTypeCode,
		  # identifikator resursa i njegov tip
		  resourceIdentifier = old_schema_file.RS_Identifier,
		  resourceIdentifierNamespace = old_schema_file.RS_Identifier_codeSpace,
		  abstract = old_schema_file.abstract,
		  # Responsible party organisationName, cotact, role
		  resp_organisationName = old_schema_file.organisationName,
		  resp_organisation_emailAddress = old_schema_file.organisation_emailAddress,
		  resp_organisation_role = old_schema_file.organisation_role,
		  # Keywords
		  keywords = old_schema_file.descriptiveKeywords,
		  #Constraints
		  useLimitation = old_schema_file.useLimitation,
		  accessConstraints = old_schema_file.accessConstraints,
		  otherConstraints = old_schema_file.otherConstraints,
		  # SpatialResolution
		  denominator = old_schema_file.denominator,
		  distance = old_schema_file.distance,
		  # resourceLanguage
		  resourceLanguage = old_schema_file.resourceLanguage,
		  #TopicCategoryes
		  inspireCategory = [old_schema_file.inspireCategory],
		  # bounding_box
		  bounding_box_w = old_schema_file.westBoundLongitude,
		  bounding_box_e = old_schema_file.eastBoundLongitude,
		  bounding_box_s = old_schema_file.southBoundLatitude,
		  bounding_box_n = old_schema_file.northBoundLatitude,
		  # temporal extend
		  t_extnt_beginPosition = old_schema_file.t_extnt_beginPosition,
		  t_extnt_endPosition =old_schema_file.t_extnt_endPosition,
		  # dist_format from srb tag
		  dist_format = old_schema_file.dist_format,
		  linkage = old_schema_file.linkage,
		  lineage = old_schema_file.lineage
		  ),
	       )
      base=os.path.basename(fxml_path)
      base= os.path.splitext(base)[0]
      yml_file_name= base  + '.yml'
      yml_file_path= ymls_dts_dir + yml_file_name
      print(yml_file_path)
      with open(yml_file_path, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
        
start_time = time.time() 

def main():
  
  template_dataset_srb_cyr= 'pygeometa/templates/dts_template_srb_cyr/'
  template_dataset_srb_lat= 'pygeometa/templates/dts_template_srb_lat/'
  template_dataset_eng = 'pygeometa/templates/dts_template_eng/'
  xml_input_dir= 'xml_input_dir/'
  xml_output_dir='xml_output_dir/'
  ymls_dts_dir='ymls_dts_dir/'
  fail_dts_dir= 'fail_dts_dir/'
  #print(glob.glob(xml_input_dir + "*.xml"))
  xmlfiles= glob.glob(xml_input_dir + "*.xml")
  data=[]
  for fxml in xmlfiles:
    makeyml(fxml, ymls_dts_dir)
  ymlfiles= glob.glob(ymls_dts_dir + "*.yml")
  for fyml in ymlfiles:
    mcf_string = fyml
    base=os.path.basename(fyml)
    base= os.path.splitext(base)[0]
    xml_file_name= base  + '.xml'
    xml_file_path= xml_output_dir + xml_file_name
    print (fyml)
    try:
      xml_string = render_template(mcf_string, schema_local=template_dataset_srb_lat)
      with open(xml_file_path, 'w') as ff:
        ff.write(xml_string)
        print('Uspeh!')
    except:
      os.rename(fyml, fail_dts_dir + base + '.yml' )
      os.rename(xml_input_dir + base  + '.xml', fail_dts_dir + xml_file_name )
      print ("Oops! " + base +' That was no valid file.  Try again...')
      continue
    
  print("--- %s seconds ---" % (time.time() - start_time))

if  __name__ =='__main__':main()